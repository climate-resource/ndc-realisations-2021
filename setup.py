import versioneer
from setuptools import setup, find_packages


PACKAGE_NAME = "ndcs"

DESCRIPTION = "Code for use in the `ndc-realisations-2021` repository"

SOURCE_DIR = "src"


setup(
    version=versioneer.get_version(),
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    packages=find_packages(SOURCE_DIR),  # no exclude as only searching in `src`
    package_dir={"": SOURCE_DIR},
)
