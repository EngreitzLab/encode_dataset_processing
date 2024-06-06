import os

import click
import pandas as pd

LAB = "/labs/jesse-engreitz/"
AWARD = "UM1HG009436"
ANNOTATION_TYPE = "element gene regulatory interaction predictions"
ORGANISM = "human"
rE2G_ALIAS_PREFIX = "jesse-engreitz:encode_re2g_predictions_"
ABC_ALIAS_PREFIX = "jesse-engreitz:abc_predictions_"
SOFTWARE_USED = "encode:rE2g_v2, encode:abc_v1.1.2"

def get_alias(cluster, dhs_hic, software_type):
    if software_type == "rE2G":
        prefix = rE2G_ALIAS_PREFIX
    elif software_type == "ABC":
        prefix = ABC_ALIAS_PREFIX
    else:
        raise Exception(f"{software_type} not supported")

    if dhs_hic:
        suffix = "_DNaseHiC"
    else:
        suffix = "_DNaseOnly"
    return f"{prefix}{cluster}{suffix}"

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
        aliases = ", ".join([get_alias(row['Cluster ID'], dhs_hic, "rE2G"), get_alias(row['Cluster ID'], dhs_hic, "ABC")])
        new_rows.append({
            "description": f"ENCODE-rE2G predictions for {row['Biosample term name']}; Donor: {get_donor(row)}",
            "lab": LAB,
            "award": AWARD,
            "annotation_type": ANNOTATION_TYPE,
            "assay_term_name": get_assay_term_name(dhs_hic),
            "organism": ORGANISM,
            "biosample_ontology": row["Biosample ontology"],
            "experimental_input": row["DNase Experiment accession"],
            "aliases": aliases,
            "software_used": SOFTWARE_USED,
            "disease_term_id": row["Disease Term ID"]
        })
    pd.DataFrame(new_rows).to_csv(output, sep='\t', index=False)

if __name__ == "__main__":
    main()
