import concurrent.futures
import os

import click
import pandas as pd
import synapseclient
from synapseclient import File, Folder

PREFIX = "encode_e2g_predictions_"
BigInteractSuffix = "_thresholded_predictions.bigInteract"
FullPredictionsSuffix = "_full_predictions.tsv.gz"
BEDPESuffix = "_thresholded_predictions.bedpe.gz"
ThresholdedPredictionsSuffix = "_thresholded_predictions.tsv.gz"

FILE_TYPES = [
    "thresholded_bigInteract",
    "thresholded_predictions",
    "full_predictions",
    "thresholded_bedpe"
]

def synapse_upload(syn_client, parent_folder, file):
    syn_file = File(file, parent=parent_folder)
    return syn_client.store(syn_file).id

def create_subfolders(syn_client, syn_proj_id):
    file_type_syn_id = {}
    project_folder = syn_client.get(syn_proj_id)
    for file_type in FILE_TYPES:
        file_type_folder = Folder(file_type, parent=project_folder)
        folder_id = syn_client.store(file_type_folder)
        file_type_syn_id[file_type] = folder_id
    return file_type_syn_id



@click.command()
@click.option("--results", "results_folder")
@click.option("--syn_proj_id")
@click.option("--metadata", help="Use filtered metadata file")
@click.option("--threads", default=100)
@click.option("--output", help="Name of output metadata file with synapse links")
def main(results_folder, syn_proj_id, metadata, threads, output):
    syn_client = synapseclient.login()
    file_type_syn_id = create_subfolders(syn_client, syn_proj_id)

    metadata_df = pd.read_csv(metadata, sep="\t")
    print(f"Using parallelization with {threads} threads")

    metadata_df["thresholded_bigInteract"] = metadata_df["Cluster"].apply(
        lambda x: os.path.join(
            results_folder, "thresholded_bigInteract", f"{PREFIX}{x}{BigInteractSuffix}"
        )
    )
    metadata_df["full_predictions"] = metadata_df["Cluster"].apply(
        lambda x: os.path.join(
            results_folder, "full_predictions", f"{PREFIX}{x}{FullPredictionsSuffix}"
        )
    )
    metadata_df["thresholded_bedpe"] = metadata_df["Cluster"].apply(
        lambda x: os.path.join(
            results_folder, "thresholded_bedpe", f"{PREFIX}{x}{BEDPESuffix}"
        )
    )
    metadata_df["thresholded_predictions"] = metadata_df["Cluster"].apply(
        lambda x: os.path.join(
            results_folder,
            "thresholded_predictions",
            f"{PREFIX}{x}{ThresholdedPredictionsSuffix}",
        )
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {}
        for idx, row in metadata_df.iterrows():
            for file_type in FILE_TYPES:
                parent_folder = syn_client.get(file_type_syn_id[file_type])
                futures[
                    executor.submit(
                        synapse_upload, syn_client, parent_folder, row[file_type]
                    )
                ] = (idx, file_type)

        for future in concurrent.futures.as_completed(futures.keys()):
            idx, file_type = futures[future]
            metadata_df.at[idx, f"{file_type}_SYNAPSE_ID"] = future.result()

    metadata_df.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    main()
