#!/bin/bash
set -e

# -d is for dry-run. s/dev/prod and remove -d flag to submit to production

# submit annotation objects
eu_register.py -m dev -p annotation -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/annotation.tsv -d

# submit full prediction files
eu_register.py -m dev -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_full_predictions.tsv -d

# submit thresholded prediction files
eu_register.py -m dev -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_predictions.tsv -d

# submit all thresholded bedpe files
eu_register.py -m dev -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_bedpe.tsv -d

# submit all thresholded bigInteract files
eu_register.py -m dev -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_bigInteract.tsv -d