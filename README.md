# Realisation of Paris Agreement pledges may limit warming to just below 2°C

Code and data related to `Realisation of Paris Agreement pledges may limit warming to just below 2°C`

The scenario files used for the MAGICCv7.5.3 climate quantification runs were 
prepared in this repository.

This includes:
* Extending Kyoto GHG emissions to 2100
* Infill scenario to produce scenarios ready for MAGICC
* Quantifying MAGICC outputs

The MAGICC runs were performed outside this repository.

## Getting Started

A conda environment is used to manage the required dependencies as some dependencies
may include compiled code. A new conda environment can be created using:

```
conda env create -n ndc-realisations-2021
conda activate ndc-realisations-2021
make conda-environment
```
