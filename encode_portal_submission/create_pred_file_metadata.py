import os
from collections import defaultdict

import click
import pandas as pd
from create_annotation import determine_if_dhs_hic, get_alias

LAB = "/labs/jesse-engreitz/"
AWARD = "UM1HG009436"
ASSEMBLY = "GRCh38"


def get_file_format(prediction_type):
    return {
        "full_predictions": "bed",
        "thresholded_predictions": "bed",
        "thresholded_bedpe": "bedpe",
        "thresholded_bigInteract": "bigInteract",
    }[prediction_type]


def get_output_type(prediction_type):
    return {
        "full_predictions": "element gene links",
        "thresholded_predictions": "thresholded element gene links",
        "thresholded_bedpe": "thresholded links",
        "thresholded_bigInteract": "thresholded links",
    }[prediction_type]

def get_file_format_type(prediction_type):
    return {
        "full_predictions": "bed3+",
        "thresholded_predictions": "bed3+",
        "thresholded_bedpe": "",
        "thresholded_bigInteract": "",
    }[prediction_type]

@click.command()
@click.option("--metadata")
@click.option("--file_stats")
@click.option("--output_folder")
def main(metadata, file_stats, output_folder):
    metadata_df = pd.read_csv(metadata, sep='\t')
    dhs_hic = determine_if_dhs_hic(metadata_df)
    file_stats_df = pd.read_csv(file_stats, sep='\t', index_col=0, names=['filename', 'md5sum', 'file_size'])
    new_rows = defaultdict(list)
    for idx, row in metadata_df.iterrows():
        for prediction_type in ["full_predictions", "thresholded_predictions", "thresholded_bedpe", "thresholded_bigInteract"]:
            filename = row[f"rE2G_{prediction_type}"]
            alias = get_alias(row['Cluster'], dhs_hic)
            new_row = {
                "dataset": alias,
                "file_format": get_file_format(prediction_type),
                "output_type": get_output_type(prediction_type),
                "award": AWARD,
                "lab": LAB,
                "md5sum": file_stats_df.loc[os.path.basename(filename)]["md5sum"],
                "file_size": file_stats_df.loc[os.path.basename(filename)]["file_size"],
                "step_run": "NA",
                "aliases": f"{alias}_{prediction_type}",
                "assembly": ASSEMBLY,
                "submitted_file_name": filename,
            }
            if new_row["file_format"] == "bed":
                new_row["file_format_type"] = get_file_format_type(prediction_type)
            new_rows[prediction_type].append(new_row)

    for prediction_type in new_rows:
        metadata_file = os.path.join(output_folder, f"meta_re2g_file_{prediction_type}.tsv")
        pd.DataFrame(new_rows[prediction_type]).to_csv(metadata_file, sep='\t', index=False)

if __name__ == "__main__":
    main()
