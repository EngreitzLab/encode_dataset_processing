#!/bin/bash
set -e

curl -L https://docs.google.com/spreadsheets/d/e/2PACX-1vRdVsXDS1GK_8kIAy1R9DNHNUK06AxgcvH8H4KHQrIjhOreMNghVT4OVZ2VNSw1_RzNeJDBgsq5XdST/pub?output=tsv > metadata/dhs_only_raw.tsv

curl -L https://docs.google.com/spreadsheets/d/e/2PACX-1vRMZDK-fBRQb1VMLvxDsJuV6ry6QUVuy0a0jLhTooKlaxTE4Fbu8xU0xQsu-fifg_gEAZ5aIs0kLLVP/pub?output=tsv > metadata/dhs_hic_raw.tsv

curl -L "https://www.encodeproject.org/report.tsv?type=Experiment&status=released&assay_title=DNase-seq&field=accession&field=biosample_ontology" | sed 1d > metadata/biosample_ontology.tsv

curl -L "https://www.encodeproject.org/report.tsv?type=Experiment&control_type%21=%2A&status=released&perturbed=false&assay_title=DNase-seq&replicates.library.biosample.disease_term_id=%2A&field=replicates.library.biosample.disease_term_id&field=replicates.library.biosample.disease_term_name&field=%40id&field=accession&field=assay_term_name&field=biosample_summary" | sed 1d > metadata/biosample_disease_status.tsv