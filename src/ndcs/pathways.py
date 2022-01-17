import scmdata
import logging
from tqdm.auto import tqdm
import json
import os

from .utils import ensure_dir_exists
from .constants import PROCESSED_DATA_DIR, NDC_TARGET_RELEASE

logger = logging.getLogger(__name__)

GLOBAL_DATABASE_META_DIR = os.path.join(
    PROCESSED_DATA_DIR, "global_emissions_meta", NDC_TARGET_RELEASE
)


def _get_latest(run, cmp_col="submission_date"):
    most_recent = run[cmp_col].max()

    # Hmmm can't filter using datetimes
    selected = scmdata.ScmRun(
        run.timeseries().loc[(run[cmp_col] == most_recent).tolist()]
    )

    if len(selected) != 1:
        selected = scmdata.ScmRun(selected.timeseries().iloc[[0], :])
        # Don't do this recursively
        # return _get_latest(selected, cmp_col="last_provided_year")

    return selected


def get_older_than(run, dt, cmp_col="submission_date"):
    # Hmmm can't filter using datetimes
    return scmdata.ScmRun(run.timeseries().loc[(run[cmp_col] < dt).tolist()])


def get_today(run, dt, cmp_col="submission_date"):
    # Hmmm can't filter using datetimes
    return scmdata.ScmRun(run.timeseries().loc[(run[cmp_col] == dt).tolist()])


def get_latest(run, unique_col="region"):
    """
    return a single timeseries for each value in `unique_col`
    """
    return run.groupby("region").map(_get_latest)


def process_ndc(latest_ndcs, conditionality, ambition, country_extension):
    emms = latest_ndcs.filter(
        conditionality=conditionality,
        ambition=ambition,
        country_extension=country_extension,
    )
    global_emms = scmdata.ScmRun(
        emms.values.sum(axis=0),
        index=emms["year"],
        columns={
            "variable": "Emissions|Total GHG excl. LULUCF",
            "unit": "Mt CO2/yr",
            "region": "World",
            "scenario": "HighNDC" if ambition == "high" else "LowNDC",
            "model": "NDC Factsheet",
            "conditionality": conditionality,
            "ambition": ambition,
            "country_extension": country_extension,
            "pathway_id": "_".join([ambition, conditionality, country_extension]),
            "global_extension": "N/A",
        },
    )

    return global_emms


def sum_country_emissions(submitted_ndcs, baseline_emms):
    submitted_countries = submitted_ndcs.get_unique_meta("region")
    submitted_countries = {
        k: submitted_ndcs.filter(region=k).get_unique_meta("submission_date", True)
        for k in submitted_countries
    }

    missing_countries = set(baseline_emms.get_unique_meta("region")) - set(
        submitted_countries.keys()
    )
    missing_countries_emms = baseline_emms.filter(
        region=missing_countries, log_if_empty=False
    )

    columns = {"variable": "Emissions|Total GHG excl. LULUCF", "region": "World"}
    for c in ["ambition", "country_extension", "conditionality", "model", "unit"]:
        columns[c] = submitted_ndcs.get_unique_meta(c, True)
    columns["scenario"] = "__".join([columns["ambition"], columns["conditionality"]])

    sum_emissions = submitted_ndcs.values.sum(
        axis=0
    ) + missing_countries_emms.values.sum(axis=0)

    return (
        scmdata.ScmRun(sum_emissions, columns=columns, index=submitted_ndcs["year"]),
        submitted_countries,
        list(missing_countries),
    )


class NDCCruncher:
    def __init__(
        self,
        output_db,
        country_emms,
        baseline_emms,
        conditionality,
        ambition,
        country_extension,
        exclude_hot_air,
    ):
        self.conditionality = conditionality
        self.ambition = ambition
        self.country_extension = country_extension
        self.exclude_hot_air = exclude_hot_air
        self.baseline_emms = baseline_emms
        self.output_db = output_db

        self.emms = country_emms.filter(
            conditionality=conditionality,
            ambition=ambition,
            country_extension=country_extension,
            exclude_hot_air=exclude_hot_air,
        )
        self.previous_step = None
        self.count = 1

    def crunch(self):
        unique_submission_dts = sorted(self.emms.get_unique_meta("submission_date"))
        logger.info(
            "Found {} unique submission dates from {} submissions".format(
                unique_submission_dts, len(self.emms)
            )
        )
        for dt in tqdm(unique_submission_dts):
            logger.info("Processing {}".format(str(dt)))
            self.process_day(dt, self.emms)

    def process_day(self, dt, emms):
        commitments_prev = self.previous_step
        if commitments_prev is None:
            commitments_prev = get_older_than(emms, dt)
            commitments_prev = get_latest(commitments_prev) or commitments_prev

        commitments_today = get_today(emms, dt).timeseries().sort_index(level="region")

        commitments_selected = commitments_prev

        # loop to incrementally select commitments made today (ordered by iso_code)
        for i in range(len(commitments_today)):
            to_add = scmdata.ScmRun(commitments_today.iloc[[i]])
            last_country = to_add.get_unique_meta("region", True)

            # Merge the selected commitments from today with the previous commitment
            commitments_selected = scmdata.run_append(
                [
                    commitments_prev.filter(
                        region=last_country, keep=False, log_if_empty=False
                    ),
                    to_add,
                ]
            )
            self._process_selected_ndcs(dt, i, commitments_selected, last_country)

            commitments_prev = commitments_selected
        self.previous_step = commitments_selected

    def _process_selected_ndcs(self, dt, i, commitments_selected, last_country):
        number_of_countries = len(commitments_selected.get_unique_meta("region"))
        assert len(commitments_selected) == number_of_countries  # Sanity check

        # Sum country emissions
        global_emms, selected_countries, missing_countries = sum_country_emissions(
            commitments_selected, self.baseline_emms
        )

        # Unique id for the pathway
        pathway_id = "{}_{}".format(str(dt), i + 1)

        # Dump emissions to database
        global_emms["last_country"] = last_country
        global_emms["pathway_id"] = pathway_id
        global_emms["pathway_num_today"] = i + 1
        global_emms["pathway_num"] = self.count
        global_emms["date"] = str(dt)
        global_emms["global_extension"] = "n/a"
        global_emms["exclude_hot_air"] = self.exclude_hot_air

        # Create a unique_scenario_name
        uniq_vars = [
            "pathway_id",
            "ambition",
            "conditionality",
            "country_extension",
            "exclude_hot_air",
        ]
        scenario = "__".join([global_emms.get_unique_meta(c, True) for c in uniq_vars])
        global_emms["scenario"] = scenario
        self.output_db.save(global_emms)

        # Dump selected countries to json
        fname = os.path.join(
            GLOBAL_DATABASE_META_DIR,
            self.ambition,
            self.conditionality,
            pathway_id,
            self.country_extension,
            "selected_countries.json",
        )
        ensure_dir_exists(fname)
        with open(fname, "w") as fh:
            json.dump(
                {
                    "selected": {k: str(v) for k, v in selected_countries.items()},
                    "missing": missing_countries,
                    "last_country": last_country,
                    "pathway_num": self.count,
                    "pathway_id": pathway_id,
                    "conditionality": self.conditionality,
                    "country_extension": self.country_extension,
                    "exclude_hot_air": self.exclude_hot_air,
                    "ambition": self.ambition,
                },
                fh,
            )
        self.count += 1
