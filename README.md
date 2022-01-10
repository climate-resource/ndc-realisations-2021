# Realisation of Paris Agreement pledges may limit warming to just below 2°C

Code and data related to `Realisation of Paris Agreement pledges may limit warming to just below 2°C`

The climate quantification runs MAGICCv7.5.4 using the scenario files created in
this repository.


The outputs from this repo are used to produce the interactive NDC factsheets as well
as the NDC quantifications. There are a few steps involved in extracting timeseries 
and producing the visualisations, but this repo focuses on the extraction and offline
processing steps to prepare  data (usually in the form of JSON) for visualisation on the 
Climate Resource website. 

This includes:
* Extracting data from excel
* Converting to a more useable format
* Infilling missing data
* Calculating regional/global pathways
* Infilling missing gases
* Running MAGICC
* Quantifying MAGICC outputs

## Getting Started

A conda environment is used to manage the required dependencies as some dependencies
may include compiled code. A new conda environment can be created using:

```
conda env create -n ndc-realisations-2021
conda activate ndc-realisations-2021
make conda-environment
```
