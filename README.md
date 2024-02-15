# encode_dataset_processing
Code to get the encode datasets that will get run through ABC + Encode-rE2G


1. conda activate encode_datasets
2. ./download_metadata.sh

```
py scripts/transform_datasets.py --metadata_file dhs_hic_raw.tsv --output_file dhs_hic.tsv
py scripts/transform_datasets.py --metadata_file dhs_only_raw.tsv --output_file dhs_only.tsv

py scripts/download_datasets.py --metadata_file dhs_hic.tsv --dataset_dir datasets/dhs_hic
py scripts/download_datasets.py --metadata_file dhs_only.tsv --dataset_dir datasets/dhs_only

snakemake --use-conda --profile slurm  # Slurm profile defined for running jobs

py scripts/generate_abc_biosamples.py --metadata_file dhs_hic.tsv --config_name biosamples_config_dhs_hic.tsv --dataset_dir datasets/dhs_hic
py scripts/generate_abc_biosamples.py --metadata_file dhs_only.tsv --config_name biosamples_config_dhs_only.tsv --dataset_dir datasets/dhs_only
```