import concurrent.futures
import os
import shutil
import subprocess
from typing import List

import click
import pandas as pd

BAM_FILE_FORMAT = (
    "https://www.encodeproject.org/files/{ENCODE_ID}/@@download/{ENCODE_ID}.bam"
)
NUM_THREADS = 20

def get_relevant_datasets(metadata_df):
    metadata_df = metadata_df[~metadata_df["DNase Run type"].isna()]
    return metadata_df


def download_cell_cluster_info(dataset_dir, row) -> None:
    biosample_name = row['Biosample term name'].replace(" ", "_")
    cluster = f"{biosample_name}_{row['DNase Experiment accession']}"
    if "Hi-C Experiment accession" in row:
        cluster += f"_{row['Hi-C File accession']}"
    cluster_dir = os.path.join(dataset_dir, cluster)

    dhs_encode_ids = [s.strip() for s in row["DNase File accession"].split(",")]
    dnase_run_types = [s.strip() for s in row["DNase Run type"].split(",")]
    download_from_encode(cluster_dir, dhs_encode_ids)
    filter_bam(cluster_dir, dhs_encode_ids, dnase_run_types)


def filter_bam(cluster_dir: str, dhs_encode_ids: List[str], dnase_run_types: List[str]):
    for i, encode_id in enumerate(dhs_encode_ids):
        filtered_file = os.path.join(cluster_dir, f"{encode_id}.bam")
        if os.path.exists(filtered_file):
            continue  # Already filtered
        
        print(f"Filtering {encode_id}")
        unfiltered_file = os.path.join(cluster_dir, f"{encode_id}_unfiltered.bam")
        if dnase_run_types[i] == "single-ended":
            subprocess.run(
            f"samtools view -b -F 780 -q30 {unfiltered_file} -o {filtered_file}.tmp", shell=True, check=True
        )
        elif dnase_run_types[i] == "paired-ended":
            subprocess.run(
            f"samtools view -b -F 1804 -q 30 -f2 {unfiltered_file} -o {filtered_file}.tmp", shell=True, check=True
        )
        else:
            print(f"dnase run type not supported: {dnase_run_types[i]}. Skipping...")
            continue
        
        os.rename(f"{filtered_file}.tmp", filtered_file)

def download_from_encode(cluster_dir, dhs_encode_ids):
    os.makedirs(cluster_dir, exist_ok=True)

    unfiltered_files = []
    for encode_id in dhs_encode_ids:
        unfiltered_file = os.path.join(cluster_dir, f"{encode_id}_unfiltered.bam")
        if os.path.exists(unfiltered_file):
            continue  # Already downloaded this item

        print(f"Downloading {encode_id}")
        dhs_download_url = BAM_FILE_FORMAT.format(ENCODE_ID=encode_id)
        subprocess.run(
            f"wget -O {unfiltered_file} {dhs_download_url}", shell=True, check=True
        )
        unfiltered_files.append(unfiltered_file)

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
