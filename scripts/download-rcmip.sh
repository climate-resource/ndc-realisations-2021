#!/bin/bash
mkdir -p data/raw/rcmip
wget \
    -O data/raw/rcmip/rcmip-emissions-annual-means-v5-1-0.csv \
    https://rcmip-protocols-au.s3-ap-southeast-2.amazonaws.com/v5.1.0/rcmip-emissions-annual-means-v5-1-0.csv
