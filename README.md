# Realisation of Paris Agreement pledges may limit warming to just below 2°C

Code and data related to `Realisation of Paris Agreement pledges may limit warming to just below 2°C`

The climate quantification runs MAGICCv7.5.3 using the scenario files created in
this repository.

This includes:
* Extending Kyoto GHG emissions to 2100
* Infill scenario to produce scenarios ready for MAGICC
* Quantifying MAGICC outputs

The magicc runs were performed outside of this repository.

## Getting Started

A conda environment is used to manage the required dependencies as some dependencies
may include compiled code. A new conda environment can be created using:

```
conda env create -n ndc-realisations-2021
conda activate ndc-realisations-2021
make conda-environment
```
