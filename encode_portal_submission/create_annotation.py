import os

import click
import pandas as pd

LAB = "/labs/jesse-engreitz/"
AWARD = "UM1HG009436"
ANNOTATION_TYPE = "element gene link predictions"
ASSAY_TERM_NAME = "DNase-seq"
ORGANISM = "human"
ALIAS_PREFIX = "jesse-engreitz:encode_re2g_predictions_"
SOFTWARE_USED = "encode:re2g_modelV2.0.0"

@click.command()
@click.option("--metadata")
@click.option("--output")
def main(metadata, output):
    metadata_df = pd.read_csv(metadata, sep='\t')
    new_rows = []
    for idx, row in metadata_df.iterrows():
        donor = os.path.basename(os.path.dirname(row["DNase Donor(s)"]))
        new_rows.append({
            "Description": f"ENCODE-rE2G predictions for {row['Biosample term name']}; Donor: {donor}",
            "lab": LAB,
            "award": AWARD,
            "annotation_type": ANNOTATION_TYPE,
            "assay_term_name": ASSAY_TERM_NAME,
            "organism": ORGANISM,
            "biosample_ontology": row["Biosample ontology"],
            "experimental_input": row["DNase Experiment accession"],
            "aliases": f"{ALIAS_PREFIX}{row['Cluster ID']}",
            "software_used": SOFTWARE_USED,
            "disease_term_id": row["Disease Term ID"]
        })
    pd.DataFrame(new_rows).to_csv(output, sep='\t', index=False)

if __name__ == "__main__":
    main()
