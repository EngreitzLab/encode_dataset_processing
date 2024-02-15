import click
import pandas as pd


def get_relevant_datasets(metadata_df):
    metadata_df = metadata_df[~metadata_df["DNase Output type"].isna()]
    return metadata_df


def get_cluster_name(row):
    biosample_name = (
        row["Biosample term name"].replace(" ", "_").replace(",", "_").replace("'", "")
    )
    cluster = f"{biosample_name}_{row['DNase Experiment accession']}"
    if "Hi-C Experiment accession" in row:
        cluster += f"_{row['Hi-C File accession']}"
    return cluster


def remove_whitespace(datasets, columns):
    for col in columns:
        datasets[col] = datasets[col].apply(lambda s: s.strip())


@click.command()
@click.option("--metadata_file", type=str, required=True)
@click.option("--output_file", type=str, required=True)
def main(metadata_file, output_file):
    metadata_df = pd.read_csv(metadata_file, sep="\t")
    relevant_datasets = get_relevant_datasets(metadata_df).copy()
    cluster_names = [get_cluster_name(row) for _, row in relevant_datasets.iterrows()]
    relevant_datasets["Cluster"] = cluster_names
    relevant_datasets.rename(
        columns={
            "DNase File accession": "DNase_ENCODE_ID",
            "DNase Output type": "DNase_Output_Type",
        },
        inplace=True,
    )

    has_hic = "Hi-C File accession" in metadata_df.columns
    relevant_columns = ["Cluster", "DNase_ENCODE_ID", "DNase_Output_Type"]
    if has_hic:
        relevant_datasets.rename(
            columns={"Hi-C File accession": "HiC_File_Accession"}, inplace=True
        )
        relevant_columns.append("HiC_File_Accession")

    remove_whitespace(relevant_datasets, relevant_columns)
    relevant_datasets[relevant_columns].to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    main()
