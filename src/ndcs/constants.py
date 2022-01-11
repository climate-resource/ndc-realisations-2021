import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
ROOT_DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DATA_DIR = os.path.join(ROOT_DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(ROOT_DATA_DIR, "processed")
PUBLIC_DATA_DIR = os.path.join(ROOT_DATA_DIR, "public")

NDC_TARGET_RELEASE = "12Nov2021a_CR"
LEAD = "Emissions|GHG excl CO2 AFOLU (AR6GWP100)"
CONTEXT = "AR6GWP100"
