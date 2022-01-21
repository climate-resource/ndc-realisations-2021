import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
ROOT_DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DATA_DIR = os.path.join(ROOT_DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(ROOT_DATA_DIR, "processed")
PUBLIC_DATA_DIR = os.path.join(ROOT_DATA_DIR, "public")

NDC_TARGET_RELEASE = "12Nov2021a_CR"
LEAD = "Emissions|GHG excl CO2 AFOLU (AR6GWP100)"
CONTEXT = "AR6GWP100"


SCENARIO_LABELS = {
    "2021-11-09_1__high__C__SSP1BL__exclude": "A",
    "2021-11-09_1__low__U__SSP1BL__exclude": "B",
    "2021-11-09_1__high__C__2030__exclude": "a",
    "2021-11-09_1__high__C__2030__include": "b",
    "2021-11-09_1__low__C__2030__exclude": "c",
    "2021-11-09_1__low__C__2030__include": "d",
    "2021-11-09_1__high__U__2030__exclude": "e",
    "2021-11-09_1__low__U__2030__exclude": "f",
    "2021-11-09_1__high__U__2030__include": "g",
    "2021-11-09_1__low__U__2030__include": "h",
    # Methane scenarios
    "2021-11-03_1__high__C__SSP1BL__exclude__fullCH4": "m",
    "2021-11-03_1__high__C__SSP1BL__exclude__conditionalCH4": "n",
    "2021-11-03_1__high__C__SSP1BL__exclude__unconditionalCH4": "o",
    # A variants
    "2021-11-09_1__high__C__constant__exclude": "A-constant",
    "2021-11-09_1__high__C__rate__exclude": "A-rate",
    "2021-11-09_1__high__C__SSP1BL__include": "A-hot air",
    "2021-11-09_1__high__C__SSP1BL-constant2050__exclude": "A-constant2050",
}

SCENARIO_LABELS_INVERT = {v: k for k, v in SCENARIO_LABELS.items()}
