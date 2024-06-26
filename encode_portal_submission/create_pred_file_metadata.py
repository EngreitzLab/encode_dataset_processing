import os
from collections import defaultdict

import click
import pandas as pd
from create_annotation import determine_if_dhs_hic, get_alias

LAB = "/labs/jesse-engreitz/"
AWARD = "UM1HG009436"
ASSEMBLY = "GRCh38"
STEP_RUNS = {
    "ABC": "encode:abc_element_gene_link_prediction_analysis_step_v2_run", 
    "rE2G": "encode:encode-re2g_enhancer_gene_predictions_step_v2_run"
}


def get_file_format(prediction_type):
    return {
        "full_predictions": "bed",
        "thresholded_predictions": "bed",
        "thresholded_bedpe": "bedpe",
        "thresholded_bigInteract": "bigInteract",
        "candidate_elements": "bed",
    }[prediction_type]


def get_output_type(prediction_type):
    return {
        "full_predictions": "element gene links",
        "thresholded_predictions": "thresholded element gene links",
        "thresholded_bedpe": "thresholded links",
        "thresholded_bigInteract": "thresholded links",
        "candidate_elements": "elements reference",
    }[prediction_type]

def get_file_format_type(prediction_type):
    return {
        "full_predictions": "bed3+",
        "thresholded_predictions": "bed3+",
        "thresholded_bedpe": "",
        "thresholded_bigInteract": "",
        "candidate_elements": "bed3+",
    }[prediction_type]

def get_derived_from(row, dhs_hic, software):
    if software == "ABC":
        return row["DNase_ENCODE_ID"]
    else:
        alias = get_alias(row['Cluster'], dhs_hic, "ABC")
        return f"{alias}_full_predictions"

@click.command()
@click.option("--metadata")
@click.option("--file_stats")
@click.option("--output_folder")
def main(metadata, file_stats, output_folder):
    metadata_df = pd.read_csv(metadata, sep='\t')
    dhs_hic = determine_if_dhs_hic(metadata_df)
    file_stats_df = pd.read_csv(file_stats, sep='\t', index_col=0, names=['filename', 'md5sum', 'file_size'])
    new_rows = defaultdict(list)
    for _, row in metadata_df.iterrows():
        for prediction_type in ["full_predictions", "thresholded_predictions", "thresholded_bedpe", "thresholded_bigInteract", "candidate_elements"]:
            for software in ["rE2G", "ABC"]:
                if prediction_type == "candidate_elements" and software == "rE2G":
                    continue
                derived_from = get_derived_from(row, dhs_hic, software)
                filename = row[f"{software}_{prediction_type}"]
                alias = get_alias(row['Cluster'], dhs_hic, software)
                new_row = {
                    "dataset": alias,
                    "file_format": get_file_format(prediction_type),
                    "output_type": get_output_type(prediction_type),
                    "award": AWARD,
                    "lab": LAB,
                    "md5sum": file_stats_df.loc[os.path.basename(filename)]["md5sum"],
                    "file_size": file_stats_df.loc[os.path.basename(filename)]["file_size"],
                    "step_run": STEP_RUNS[software],
                    "aliases": f"{alias}_{prediction_type}",
                    "assembly": ASSEMBLY,
                    "submitted_file_name": filename,
                    "derived_from": derived_from
                }
                if new_row["file_format"] == "bed":
                    new_row["file_format_type"] = get_file_format_type(prediction_type)
                new_rows[prediction_type].append(new_row)

    for prediction_type in new_rows:
        metadata_file = os.path.join(output_folder, f"meta_file_{prediction_type}.tsv")
        pd.DataFrame(new_rows[prediction_type]).to_csv(metadata_file, sep='\t', index=False)

if __name__ == "__main__":
    main()
