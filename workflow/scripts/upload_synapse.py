import concurrent.futures
import os
from enum import Enum

import click
import pandas as pd
import synapseclient
from synapseclient import File, Folder


class PredType(Enum):
    rE2G = 1
    ABC = 2

E2G_PREFIX = "encode_e2g_predictions_"
ABC_PREFIX = "abc_predictions_"

FILE_TYPES = {
    "thresholded_bigInteract": "_thresholded_predictions.bigInteract",
    "thresholded_predictions": "_thresholded_predictions.tsv.gz",
    "full_predictions": "_full_predictions.tsv.gz",
    "thresholded_bedpe": "_thresholded_predictions.bedpe.gz"
}

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
@click.option('--pred_type', type=click.Choice([e.name for e in PredType]))
@click.option("--threads", default=100)
def main(results_folder, syn_proj_id, metadata, pred_type, threads):
    pred_type = PredType[pred_type]
    syn_client = synapseclient.login()
    file_type_syn_id = create_subfolders(syn_client, syn_proj_id)

    metadata_df = pd.read_csv(metadata, sep="\t")
    print(f"Using parallelization with {threads} threads")
    for file_type, suffix in FILE_TYPES.items():
        if pred_type == pred_type.rE2G: 
            metadata_df[f"{pred_type.name}_{file_type}"] = metadata_df["Cluster"].apply(
                lambda x: os.path.join(
                    results_folder, file_type, f"{E2G_PREFIX}{x}{suffix}"
                )
            )
        else:
            metadata_df[f"{pred_type.name}_{file_type}"] = metadata_df["Cluster"].apply(
                lambda x: os.path.join(
                    results_folder, x, "Predictions", f"{ABC_PREFIX}{x}{suffix}"
                )
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {}
        for idx, row in metadata_df.iterrows():
            for file_type in FILE_TYPES:
                parent_folder = syn_client.get(file_type_syn_id[file_type])
                futures[
                    executor.submit(
                        synapse_upload, syn_client, parent_folder, row[f"{pred_type.name}_{file_type}"]
                    )
                ] = (idx, file_type)

        for future in concurrent.futures.as_completed(futures.keys()):
            idx, file_type = futures[future]
            metadata_df.at[idx, f"{pred_type.name}_{file_type}_SYNAPSE_ID"] = future.result()

    metadata_df.to_csv(metadata, sep="\t", index=False)


if __name__ == "__main__":
    main()
