# encode_dataset_processing
Code to get the encode datasets that will get run through ABC + Encode-rE2G


1. conda activate encode_datasets (built from workflow/envs/env.yml)
2. ./download_metadata.sh

## 1. Prepare Biosample Config
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

## 2. Run rE2G
Run ENCODE_rE2G pipeline separately 
Generate the 4 encode files for each biosample (using Andreas' pipeline)

## 3. Convert ABC output into ENCODE format
```
# reformat the prediction files and generate bigInteract and bedpe
# (Uncomment `get_bigInteract`, `get_bedpe`, and `get_candidate_elements` lines in Snakemake All rule)
snakemake --use-conda --profile slurm 
```

Compute ABC file stats, which is needed for ENCODE portal submission
```
py workflow/scripts/compute_abc_file_stats.py --results_dir results/ --output_file encode_portal_submission/results/abc_file_stats.tsv
```

Add peak file column to metadata (Prediction file columns are added in the next step when uploading to synapse)
```
py workflow/scripts/update_metadata.py add_abc_peaks --metadata metadata/dhs_only.tsv --results results/dhs_only/
py workflow/scripts/update_metadata.py add_abc_peaks --metadata metadata/dhs_hic.tsv --results results/dhs_hic/
```

## 4. Upload to Synapse
Synapse upload as an intermediate step for the ENCODE Submission 
Requires Synapse authentication to be setup: https://python-docs.synapse.org/tutorials/authentication/#use-synapseconfig
Side effect: Updates metadata to include prediction file columns and prediction synapse ids
```
py workflow/scripts/upload_synapse.py --results /oak/stanford/groups/engreitz/Projects/Benchmarking/Revisions/Predictors/ENCODE-rE2G/dhs_only --syn_proj_id syn55082465 --metadata metadata/dhs_only.tsv --pred_type rE2G
py workflow/scripts/upload_synapse.py --results /oak/stanford/groups/engreitz/Projects/Benchmarking/Revisions/Predictors/ENCODE-rE2G/dhs_hic --syn_proj_id syn55173025 --metadata metadata/dhs_hic.tsv --pred_type rE2G

py workflow/scripts/upload_synapse.py --results results/dhs_only/ --syn_proj_id syn58711253 --metadata metadata/dhs_only.tsv --pred_type ABC
py workflow/scripts/upload_synapse.py --results results/dhs_hic/ --syn_proj_id syn58711235 --metadata metadata/dhs_hic.tsv --pred_type ABC

# Modify original raw metadata tsv file with SYNAPSE columns and other columns needed for ENCODE portal submission (ontology and disease)
py workflow/scripts/update_metadata.py update_orig --orig_metadata metadata/dhs_only_raw.tsv --biosample_ontology metadata/biosample_ontology.tsv --biosample_disease metadata/biosample_disease_status.tsv --metadata_synapse metadata/dhs_only.tsv 
py workflow/scripts/update_metadata.py update_orig --orig_metadata metadata/dhs_hic_raw.tsv --biosample_ontology metadata/biosample_ontology.tsv --biosample_disease metadata/biosample_disease_status.tsv --metadata_synapse metadata/dhs_hic.tsv
```


## 5. ENCODE Portal Submission
DHS-only supported  

# Create annotation file
py encode_portal_submission/create_annotation.py --metadata metadata/dhs_only_raw.tsv --output encode_portal_submission/results/dhs_only/annotation.tsv
<!-- py encode_portal_submission/create_annotation.py --metadata metadata/dhs_hic_raw.tsv --output encode_portal_submission/results/dhs_hic/annotation.tsv -->

# Create file object tsv file for each of the 5 file uploads 
# Each file upload contains both rE2G and ABC predictions (with exception of Peaks file only containing ABC results)
py encode_portal_submission/create_pred_file_metadata.py --metadata metadata/dhs_only.tsv --file_stats encode_portal_submission/results/all_combined_file_stats.tsv --output_folder encode_portal_submission/results/dhs_only
<!-- py encode_portal_submission/create_pred_file_metadata.py --metadata metadata/dhs_hic.tsv --file_stats encode_portal_submission/results/combined_file_stats.tsv.gz --output_folder encode_portal_submission/results/dhs_hic -->


./submit_to_portal.sh