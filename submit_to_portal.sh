#!/bin/bash
set -e

# # submit annotation objects
# eu_register.py -m prod -p annotation -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/annotation.tsv

# # submit full prediction files
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_full_predictions.tsv 

# # submit thresholded prediction files
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_predictions.tsv 

# # submit all thresholded bedpe files
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_bedpe.tsv 

# # submit all thresholded bigInteract files
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_thresholded_bigInteract.tsv 

# # submit all candidate element files
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/meta_file_candidate_elements.tsv 


# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/patches/meta_file_full_predictions.tsv --patch
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/patches/meta_file_thresholded_predictions.tsv --patch
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/patches/meta_file_thresholded_bedpe.tsv  --patch
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/patches/meta_file_thresholded_bigInteract.tsv --patch
# eu_register.py -m prod -p file -i /oak/stanford/groups/engreitz/Users/atan5133/encode_dataset_processing/encode_portal_submission/results/dhs_only/patches/meta_file_candidate_elements.tsv --patch
