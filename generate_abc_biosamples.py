import os

import click
import pandas as pd
from download_datasets import get_relevant_datasets, get_cluster_name

CONFIG_TEMPLATE_FILE = "https://raw.githubusercontent.com/broadinstitute/ABC-Enhancer-Gene-Prediction/dev/config/config_biosamples_template.tsv"
HIC_DOWNLOAD_FORMAT = (
    "https://www.encodeproject.org/files/{ENCODE_ID}/@@download/{ENCODE_ID}.hic"
)

@click.command()
@click.option("--metadata_file", type=str, required=True)
@click.option("--base_dataset_dir", type=str, default="datasets/")
@click.option("--config_name", type=str, default="biosamples_config.tsv")
def main(metadata_file, base_dataset_dir, config_name):
    metadata_filename = os.path.basename(metadata_file)
    metadata_label = metadata_filename.split(".")[0]
    dataset_dir = os.path.abspath(os.path.join(base_dataset_dir, metadata_label))

    biosamples = pd.read_csv(CONFIG_TEMPLATE_FILE, sep="\t")

    metadata_df = pd.read_csv(metadata_file, sep="\t")
    relevant_datasets = get_relevant_datasets(metadata_df)
    for i, row in relevant_datasets.iterrows():
        cluster_name = get_cluster_name(row)
        cluster_folder = os.path.join(dataset_dir, cluster_name)
        dhs_encode_ids = [s.strip() for s in row["DNase File accession"].split(",")]
        dhs_files = [os.path.join(cluster_folder, f"{dhs_encode_id}_sorted.bam") for dhs_encode_id in dhs_encode_ids]
        biosample = {
            "biosample": cluster_name,
            "DHS": ",".join(dhs_files),
            "default_accessibility_feature": "DHS",
            "HiC_file": HIC_DOWNLOAD_FORMAT.format(ENCODE_ID=row["Hi-C File accession"]),
            "HiC_type": "hic",
            "HiC_resolution": 5000,
        }
        biosamples.loc[i] = biosample

    biosamples.to_csv(config_name, sep="\t", index=False)
    print(f"Generate config: {config_name}")


if __name__ == "__main__":
    main()
