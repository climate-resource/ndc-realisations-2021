.PHONY: clean data lint sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = cr-public-data
BUCKET_PREFIX = ndc
PROFILE = cr-prod

ifndef CONDA_PREFIX
$(error Conda environment not active. Activate your conda environment before using this Makefile.)
else
ifeq ($(CONDA_DEFAULT_ENV),base)
$(error Do not install to conda base environment. Activate a different conda environment and rerun make. A new environment can be created with e.g. `conda create --name ndc-realisations-2021`))
endif
VENV_DIR=$(CONDA_PREFIX)
endif

PYTHON_INTERPRETER = $(VENV_DIR)/bin/python
BASH = /bin/bash

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
.PHONY: conda-environment
conda-environment: $(VENV_DIR)
$(VENV_DIR): setup.py environment.yml
	mamba env update --name $(CONDA_DEFAULT_ENV) -f environment.yml
	$(VENV_DIR)/bin/pip install -e .
	$(VENV_DIR)/bin/jupyter nbextension enable --py widgetsnbextension


## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(PROFILE))
	aws s3 sync data/public/ s3://$(BUCKET)/$(BUCKET_PREFIX)/
else
	aws-vault exec $(PROFILE) -- aws s3 sync data/public/ s3://$(BUCKET)/$(BUCKET_PREFIX)/
endif


# Uploads content to s3 and deletes any files not in data/public
sync_data_to_s3_and_delete_old:
ifeq (default,$(PROFILE))
	aws s3 sync --delete data/public/ s3://$(BUCKET)/$(BUCKET_PREFIX)/
else
	aws-vault exec $(PROFILE) -- aws s3 sync --delete data/public/ s3://$(BUCKET)/$(BUCKET_PREFIX)/
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(PROFILE))
	aws s3 sync s3://$(BUCKET)/$(BUCKET_PREFIX)/ data/public/
else
	aws-vault exec $(PROFILE) -- aws s3 sync s3://$(BUCKET)/$(BUCKET_PREFIX)/ data/public/
endif


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


.PHONY: format-notebooks
format-notebooks: $(VENV_DIR)  ## format the notebooks
	$(VENV_DIR)/bin/black-nb notebooks


.PHONY: test
test: $(VENV_DIR)  ## format the notebooks
	$(VENV_DIR)/bin/pytest .


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
