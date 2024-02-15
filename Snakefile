from snakemake.utils import min_version
import os
import pandas as pd
min_version("7.0")
configfile: "config/config.yml"
conda: "mamba"

RESULTS_DIR = config["results_dir"]
BASE_DATASET_DIR = config["base_dataset_dir"]

DHS_HIC_DF = pd.read_csv(config["dhs_hic_metadata"], sep="\t")
DHS_ONLY_DF = pd.read_csv(config["dhs_only_metadata"], sep="\t")

def get_bai_files(df, df_type):
	bai_files = []
	for _, row in df.iterrows():
		dhs_encode_ids = row["DNase_ENCODE_ID"].split(", ")
		for dhs_encode_id in dhs_encode_ids:
			file = os.path.join(BASE_DATASET_DIR, df_type, row["Cluster"], f"{dhs_encode_id}_sorted.bam.bai")
			bai_files.append(file)
	return bai_files


rule all:
	input:
		# get_bai_files(DHS_HIC_DF, "dhs_hic"),
		get_bai_files(DHS_ONLY_DF, "dhs_only")
	

rule sort_and_index_bam: 
	input:
		bam_file = os.path.join(BASE_DATASET_DIR, "{DF_TYPE}", "{CLUSTER}", "{DHS_ENCODE_ID}.bam")
	conda:
		"env.yml"
	output: 
		sorted_file = os.path.join(BASE_DATASET_DIR, "{DF_TYPE}", "{CLUSTER}", "{DHS_ENCODE_ID}_sorted.bam"),
		bai_file = os.path.join(BASE_DATASET_DIR, "{DF_TYPE}", "{CLUSTER}", "{DHS_ENCODE_ID}_sorted.bam.bai")
	threads: 4
	resources:
		mem_mb=8000
	shell: 
		"""
		samtools sort -@ 4 -m 1G {input.bam_file} -o {output.sorted_file}
		samtools index -@ 4 {output.sorted_file}
		"""