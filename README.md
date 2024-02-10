# encode_dataset_processing
Code to get the encode datasets that will get run through ABC + Encode-rE2G


1. conda activate encode_datasets
2. ./download_metadata.sh
3. py download_datasets.py --metadata_file dhs_hic.tsv
4. py generate_abc_biosamples.py --metadata_file dhs_hic.tsv --config_name biosamples_config_dhs_hic.tsv
