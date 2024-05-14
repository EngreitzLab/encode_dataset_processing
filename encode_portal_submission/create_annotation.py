import os

import click
import pandas as pd

LAB = "/labs/jesse-engreitz/"
AWARD = "UM1HG009436"
ANNOTATION_TYPE = "element gene link predictions"
ORGANISM = "human"
ALIAS_PREFIX = "jesse-engreitz:encode_re2g_predictions_"
SOFTWARE_USED = "encode:re2g_modelV2.0.0"

def get_alias(cluster, dhs_hic):
    if dhs_hic:
        suffix = "_DNaseHiC"
    else:
        suffix = "_DNaseOnly"
    return f"{ALIAS_PREFIX}{cluster}{suffix}"

def get_assay_term_name(dhs_hic):
    if dhs_hic:
        return "DNase-seq,HiC"
    return "DNase-seq"

def get_donor(row):
    donor = row["DNase Donor(s)"]
    if pd.isna(donor):
        return "NA"
    return os.path.basename(os.path.dirname(donor))

def determine_if_dhs_hic(metadata_df):
    cols = set(metadata_df.columns)
    if "HiC_File_Accession" in cols or "Hi-C Experiment accession" in cols:
        return True
    return False


@click.command()
@click.option("--metadata")
@click.option("--output")
def main(metadata, output):
    metadata_df = pd.read_csv(metadata, sep='\t')
    dhs_hic = determine_if_dhs_hic(metadata_df)
    new_rows = []
    for idx, row in metadata_df.iterrows():
        new_rows.append({
            "Description": f"ENCODE-rE2G predictions for {row['Biosample term name']}; Donor: {get_donor(row)}",
            "lab": LAB,
            "award": AWARD,
            "annotation_type": ANNOTATION_TYPE,
            "assay_term_name": get_assay_term_name(dhs_hic),
            "organism": ORGANISM,
            "biosample_ontology": row["Biosample ontology"],
            "experimental_input": row["DNase Experiment accession"],
            "aliases": get_alias(row['Cluster ID'], dhs_hic),
            "software_used": SOFTWARE_USED,
            "disease_term_id": row["Disease Term ID"]
        })
    pd.DataFrame(new_rows).to_csv(output, sep='\t', index=False)

if __name__ == "__main__":
    main()
