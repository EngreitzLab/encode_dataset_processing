import click
import pandas as pd

"""
Add score column
Replace Cell Type with Biosample term id
Make first row start with #
"""


@click.command()
@click.option("--predictions")
@click.option("--metadata")
@click.option("--output")
def main(predictions, metadata, output):
	metadata_df = pd.read_csv(metadata, sep='\t')
	pred = pd.read_csv(predictions, sep='\t')
	pred["Score"] = pred["ABC.Score"]
	pred.rename(columns={'chr': '#chr'}, inplace=True)
	cluster_id = pred["CellType"].iloc[0]
	pred["CellType"] = metadata_df[metadata_df["Cluster ID"] == f"{cluster_id}"].iloc[0]["Biosample term name"]
	pred.to_csv(output, sep='\t', index=False)

if __name__ == "__main__":
	main()