# encode_dataset_processing
Code to get the encode datasets that will get run through ABC + Encode-rE2G


1. conda activate encode_datasets (built from workflow/envs/env.yml)
2. ./download_metadata.sh

## Prepare Biosample Config
```
py workflow/scripts/transform_datasets.py --metadata_file metadata/dhs_hic_raw.tsv --output_file metadata/dhs_hic.tsv
py workflow/scripts/transform_datasets.py --metadata_file metadata/dhs_only_raw.tsv --output_file metadata/dhs_only.tsv

py workflow/scripts/download_datasets.py --metadata_file metadata/dhs_hic.tsv --dataset_dir datasets/dhs_hic
py workflow/scripts/download_datasets.py --metadata_file metadata/dhs_only.tsv --dataset_dir datasets/dhs_only

# Sort and index bam (Uncomment `get_bai_files` lines in all rule)
snakemake --use-conda --profile slurm  # Slurm profile defined for running jobs

py workflow/scripts/generate_abc_biosamples.py --metadata_file metadata/dhs_hic.tsv --config_name biosamples_config_dhs_hic.tsv --dataset_dir datasets/dhs_hic
py workflow/scripts/generate_abc_biosamples.py --metadata_file metadata/dhs_only.tsv --config_name biosamples_config_dhs_only.tsv --dataset_dir datasets/dhs_only
```

## Run rE2G
Run ENCODE_rE2G pipeline separately 
Generate the 4 encode files for each biosample (using Andreas' pipeline)

## Convert ABC output into ENCODE format
```
# reformat the prediction files and generate bigInteract and bedpe
# (Uncomment `get_bigInteract` and `get_bedpe` lines in Snakemake All rule)
snakemake --use-conda --profile slurm 
```

## Upload to Synapse
Requires Synapse authentication to be setup: https://python-docs.synapse.org/tutorials/authentication/#use-synapseconfig
```
py workflow/scripts/upload_synapse.py --results /scratch/users/agschwin/encode_re2g/dhs_only/ --syn_proj_id syn55082465 --metadata metadata/dhs_only.tsv --pred_type rE2G
py workflow/scripts/upload_synapse.py --results /scratch/users/agschwin/encode_re2g/dhs_hic/ --syn_proj_id syn55173025 --metadata metadata/dhs_hic.tsv --pred_type rE2G

py workflow/scripts/upload_synapse.py --results results/dhs_only/ --syn_proj_id syn58711253 --metadata metadata/dhs_only.tsv --pred_type ABC
py workflow/scripts/upload_synapse.py --results results/dhs_hic/ --syn_proj_id syn58711235 --metadata metadata/dhs_hic.tsv --pred_type ABC

# Modify original raw metadata tsv file with column of synapse ids
py workflow/scripts/update_metadata.py --orig_metadata metadata/dhs_only_raw.tsv --biosample_ontology metadata/biosample_ontology.tsv --biosample_disease metadata/biosample_disease_status.tsv --metadata_synapse metadata/dhs_only.tsv 
py workflow/scripts/update_metadata.py --orig_metadata metadata/dhs_hic_raw.tsv --biosample_ontology metadata/biosample_ontology.tsv --biosample_disease metadata/biosample_disease_status.tsv --metadata_synapse metadata/dhs_hic.tsv
```


## ENCODE Portal Submission

# Create annotation file. Include documents field
py encode_portal_submission/create_annotation.py --metadata metadata/dhs_only_raw.tsv --output dhs_only_annotation.tsv

# Create file object tsv file for each of the 4 file uploads
# Step run to indicate file provenance 