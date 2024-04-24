# encode_dataset_processing
Code to get the encode datasets that will get run through ABC + Encode-rE2G


1. conda activate encode_datasets
2. ./download_metadata.sh

```
py workflow/scripts/transform_datasets.py --metadata_file metadata/dhs_hic_raw.tsv --output_file metadata/dhs_hic.tsv
py workflow/scripts/transform_datasets.py --metadata_file metadata/dhs_only_raw.tsv --output_file metadata/dhs_only.tsv

py workflow/scripts/download_datasets.py --metadata_file metadata/dhs_hic.tsv --dataset_dir datasets/dhs_hic
py workflow/scripts/download_datasets.py --metadata_file metadata/dhs_only.tsv --dataset_dir datasets/dhs_only

# Sort and index bam
snakemake --use-conda --profile slurm  # Slurm profile defined for running jobs

py workflow/scripts/generate_abc_biosamples.py --metadata_file metadata/dhs_hic.tsv --config_name biosamples_config_dhs_hic.tsv --dataset_dir datasets/dhs_hic
py workflow/scripts/generate_abc_biosamples.py --metadata_file metadata/dhs_only.tsv --config_name biosamples_config_dhs_only.tsv --dataset_dir datasets/dhs_only
```


Upload to Synapse
Requires Synapse authentication to be setup: https://python-docs.synapse.org/tutorials/authentication/#use-synapseconfig
```
py workflow/scripts/upload_synapse.py --results /scratch/users/agschwin/encode_re2g/dhs_only/ --syn_proj_id syn55082465 --metadata dhs_only.tsv --output dhs_only_w_synapse.tsv
py workflow/scripts/upload_synapse.py --results /scratch/users/agschwin/encode_re2g/dhs_hic/ --syn_proj_id syn55173025 --metadata dhs_hic.tsv --output dhs_hic_w_synapse.tsv

py workflow/scripts/update_metadata.py --orig_metadata dhs_only_raw.tsv --metadata_synapse dhs_only_w_synapse.tsv  --new_metadata dhs_only_raw_synapse.tsv
py workflow/scripts/update_metadata.py --orig_metadata dhs_hic_raw.tsv --metadata_synapse dhs_hic_w_synapse.tsv  --new_metadata dhs_hic_raw_synapse.tsv
```

Upload ABC to Synapse
py workflow/scripts/
