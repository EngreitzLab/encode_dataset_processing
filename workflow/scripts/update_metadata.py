import os

import click
import pandas as pd


def get_synapse_columns(columns):
    synapse_cols = []
    for col in columns:
        if "SYNAPSE_ID" in col:
            synapse_cols.append(col)
              
    return synapse_cols

@click.command()
@click.option("--orig_metadata")
@click.option("--biosample_ontology")
@click.option("--biosample_disease")
@click.option("--metadata_synapse")
def main(orig_metadata, biosample_ontology, biosample_disease, metadata_synapse):
    orig_metadata_df = pd.read_csv(orig_metadata, sep='\t')
    if "Cluster ID" in orig_metadata_df.columns:
        raise Exception("Already merged the original metadata. If you wish to re-merge, redownload raw metadata")
    biosample_ontology_df = pd.read_csv(biosample_ontology, sep='\t')
    biosample_disease_df = pd.read_csv(biosample_disease, sep='\t').rename(columns={"replicates.library.biosample.disease_term_id": "Disease Term ID"})
    metadata_syn_df = pd.read_csv(metadata_synapse, sep='\t')
    metadata_syn_df.rename(columns={"Cluster": "Cluster ID"}, inplace=True)

    if "HiC_File_Accession" in metadata_syn_df.columns:
        left_col = "Hi-C File accession"
        right_col = "HiC_File_Accession"
    else:
        left_col = 'DNase File accession'
        right_col = 'DNase_ENCODE_ID'

    merged_df = orig_metadata_df.merge(biosample_ontology_df, left_on="DNase Experiment accession", right_on="Accession", how="left")
    merged_df = merged_df.merge(biosample_disease_df, left_on="DNase Experiment accession", right_on="Accession", how="left")
    merged_df = merged_df.merge(metadata_syn_df, left_on=left_col, right_on=right_col, how="left", suffixes=(None, "_y"))
    columns = ["Cluster ID"] + orig_metadata_df.columns.to_list() + ["Biosample ontology", "Disease Term ID"] + get_synapse_columns(metadata_syn_df.columns.to_list())
    assert len(merged_df) == len(orig_metadata_df), "Cannot properly merge metadata 1:1"
    merged_df.fillna("NA", inplace=True)
    merged_df[columns].to_csv(orig_metadata, sep='\t', index=False)


if __name__ == "__main__":
    main()
