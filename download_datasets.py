import concurrent.futures
import glob
import os
import subprocess
from typing import List

import click
import pandas as pd

BAM_DOWNLOAD_FORMAT = (
    "https://www.encodeproject.org/files/{ENCODE_ID}/@@download/{ENCODE_ID}.bam"
)
NUM_THREADS = 20


def get_relevant_datasets(metadata_df):
    metadata_df = metadata_df[~metadata_df["DNase Output type"].isna()]
    return metadata_df


def get_cluster_name(row):
    biosample_name = row["Biosample term name"].replace(" ", "_").replace(",", "_").replace("'","")
    cluster = f"{biosample_name}_{row['DNase Experiment accession']}"
    if "Hi-C Experiment accession" in row:
        cluster += f"_{row['Hi-C File accession']}"
    return cluster


def download_cell_cluster_info(dataset_dir, row) -> None:
    cluster = get_cluster_name(row)
    cluster_dir = os.path.join(dataset_dir, cluster)
    # Delete tmp files if they exist. That usually signifies an incomplete sort/index run
    delete_tmp_files(cluster_dir)

    dhs_encode_ids = [s.strip() for s in row["DNase File accession"].split(",")]
    dnase_output_types = [s.strip() for s in row["DNase Output type"].split(",")]
    unfiltered_files = download_from_encode(cluster_dir, dhs_encode_ids)
    filtered_files = filter_bam(
        cluster_dir, dhs_encode_ids, dnase_output_types, unfiltered_files
    )
    sort_and_index_bam(cluster_dir, dhs_encode_ids, filtered_files)
    delete_tmp_files(cluster_dir)


def delete_tmp_files(cluster_dir: str):
    # Construct full pattern path
    full_pattern = os.path.join(cluster_dir, "*tmp*")

    # Find all files in the directory that match the pattern
    files_deleted = len(glob.glob(full_pattern))
    for file in glob.glob(full_pattern):
        os.remove(file)

    if files_deleted:
        print(f"Deleted {files_deleted} tmp files in {cluster_dir}")


def sort_and_index_bam(
    cluster_dir: str, dhs_encode_ids: List[str], filtered_files: List[str]
):
    for i, encode_id in enumerate(dhs_encode_ids):
        sorted_bam = os.path.join(cluster_dir, f"{encode_id}_sorted.bam")
        indexed_bam = f"{sorted_bam}.bai"
        if os.path.exists(sorted_bam) and os.path.exists(indexed_bam):
            continue  # Already sorted and indexed

        filtered_file = filtered_files[i]
        print(f"Sorting and indexing {filtered_file}")
        subprocess.run(
            f"samtools sort {filtered_file} -o {sorted_bam} && samtools index {sorted_bam}",
            shell=True,
            check=True,
        )


def filter_bam(
    cluster_dir: str,
    dhs_encode_ids: List[str],
    dnase_output_types: List[str],
    unfiltered_files: List[str],
):
    filtered_files = []
    for i, encode_id in enumerate(dhs_encode_ids):
        filtered_file = os.path.join(cluster_dir, f"{encode_id}.bam")
        filtered_files.append(filtered_file)
        if os.path.exists(filtered_file):
            continue  # Already filtered

        unfiltered_file = unfiltered_files[i]
        print(f"Filtering {unfiltered_file}")
        if dnase_output_types[i] == "unfiltered alignments":
            subprocess.run(
                f"samtools view -b -F 780 -q30 {unfiltered_file} -o {filtered_file}.tmp",
                shell=True,
                check=True,
            )
        elif dnase_output_types[i] == "alignments":
            subprocess.run(
                f"samtools view -b -F 1804 -q 30 -f2 {unfiltered_file} -o {filtered_file}.tmp",
                shell=True,
                check=True,
            )
        else:
            print(
                f"DNase Output type not supported: {dnase_output_types[i]}. Skipping..."
            )
            continue

        os.rename(f"{filtered_file}.tmp", filtered_file)
    return filtered_files


def download_from_encode(cluster_dir, dhs_encode_ids):
    os.makedirs(cluster_dir, exist_ok=True)

    unfiltered_files = []
    for encode_id in dhs_encode_ids:
        unfiltered_file = os.path.join(cluster_dir, f"{encode_id}_unfiltered.bam")
        unfiltered_file_tmp = unfiltered_file + ".tmp"
        unfiltered_files.append(unfiltered_file)
        if os.path.exists(unfiltered_file):
            continue  # Already downloaded this item

        print(f"Downloading {unfiltered_file}")
        dhs_download_url = BAM_DOWNLOAD_FORMAT.format(ENCODE_ID=encode_id)
        subprocess.run(
            f"wget -O {unfiltered_file_tmp} {dhs_download_url}", shell=True, check=True
        )
        os.rename(unfiltered_file_tmp, unfiltered_file)

    return unfiltered_files


@click.command()
@click.option("--metadata_file", type=str, required=True)
@click.option("--base_dataset_dir", type=str, default="datasets/")
def main(metadata_file, base_dataset_dir):
    metadata_filename = os.path.basename(metadata_file)
    metadata_label = metadata_filename.split(".")[0]
    dataset_dir = os.path.join(base_dataset_dir, metadata_label)
    os.makedirs(dataset_dir, exist_ok=True)

    metadata_df = pd.read_csv(metadata_file, sep="\t")

    relevant_datasets = get_relevant_datasets(metadata_df)

    print(f"{len(relevant_datasets)} datasets to download")
    print(f"Using parallelization with {NUM_THREADS} threads")

    # Download datasets in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {
            executor.submit(download_cell_cluster_info, dataset_dir, row)
            for _, row in relevant_datasets.iterrows()
        }

        for future in concurrent.futures.as_completed(futures):
            future.result()  # raises Exceptions from threads

    print("Downloaded all the datasets")


if __name__ == "__main__":
    main()
