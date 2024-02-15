#!/bin/bash
set -e

curl -L https://docs.google.com/spreadsheets/d/e/2PACX-1vRdVsXDS1GK_8kIAy1R9DNHNUK06AxgcvH8H4KHQrIjhOreMNghVT4OVZ2VNSw1_RzNeJDBgsq5XdST/pub?output=tsv > dhs_only_raw.tsv

curl -L https://docs.google.com/spreadsheets/d/e/2PACX-1vRMZDK-fBRQb1VMLvxDsJuV6ry6QUVuy0a0jLhTooKlaxTE4Fbu8xU0xQsu-fifg_gEAZ5aIs0kLLVP/pub?output=tsv > dhs_hic_raw.tsv