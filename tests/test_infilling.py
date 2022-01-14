import numpy as np
import pytest
import scmdata
import os

from ndcs.constants import PROCESSED_DATA_DIR, NDC_TARGET_RELEASE, LEAD
from ndcs.infilling import EqualQuantileWalk_MM, kyoto_ghg_exclude_co2_vars, calc_ghg

YEARS_TO_INFILL = [2015] + list(range(2020, 2100 + 1, 5))


@pytest.fixture()
def infilling_database():
    sr15_data_cleaned = scmdata.ScmRun(
        os.path.join(PROCESSED_DATA_DIR, "sr15_data.csv")
    )
    return (
        sr15_data_cleaned.filter(year=YEARS_TO_INFILL)
        .drop_meta(["climate_model", "id", "todo"])
        .copy()
        .to_iamdataframe()
    )


@pytest.fixture()
def scenarios():
    extended_scenario_all = scmdata.ScmRun(
        os.path.join(
            PROCESSED_DATA_DIR,
            "global_emissions_pathways",
            NDC_TARGET_RELEASE,
            "emissions_ghg_extended.csv",
        )
    ).drop_meta(
        [
            "global_extension",
            "ambition",
            "conditionality",
            "country_extension",
            "date",
            "exclude_hot_air",
            "last_country",
            "pathway_id",
            "pathway_num",
            "pathway_num_today",
        ]
    )
    return extended_scenario_all.filter(
        scenario=[
            "2021-11-09_1__high__C__SSP1BL__exclude",
            "2021-11-09_1__low__U__SSP1BL__exclude",
        ],
        year=YEARS_TO_INFILL,
    )


@pytest.mark.parametrize("q", [0.25, 0.244, 0.5])
def test_mm_infilling(infilling_database, q):
    cruncher = EqualQuantileWalk_MM(infilling_database, kyoto_ghg_exclude_co2_vars)

    infilled_scenario = scmdata.ScmRun(
        infilling_database.filter(variable=LEAD)
    ).quantiles_over(("model", "scenario"), quantiles=[q])
    infilled_scenario["scenario"] = "Unknown"
    infilled_scenario["model"] = "Unknown"
    infilled_scenario = scmdata.ScmRun(infilled_scenario).copy().to_iamdataframe()

    for v in kyoto_ghg_exclude_co2_vars:
        infiller = cruncher.derive_relationship(v, [LEAD], include_quantile=True)

        infilled_scenario.append(infiller(infilled_scenario), inplace=True)

    infilled_scenario = scmdata.ScmRun(infilled_scenario)
    assert len(infilled_scenario.filter(variable=kyoto_ghg_exclude_co2_vars)) == len(
        kyoto_ghg_exclude_co2_vars
    )

    # The xth quantile of the GHG should be close (but not the same) to the xth quantile of the bottom up
    # Within 5ish %
    np.testing.assert_allclose(
        infilled_scenario.filter(variable="*|Quantile", year=2100).values,
        q,
        atol=0.05,
    )

    # Check that the bottom up GHG is the same
    infilled_ghg = calc_ghg(infilled_scenario, kyoto_ghg_exclude_co2_vars)
    infilled_cum_ghg = infilled_ghg.values.sum()
    scenario_cum_ghg = infilled_scenario.filter(variable=LEAD).values.sum()

    np.testing.assert_allclose(infilled_cum_ghg, scenario_cum_ghg, rtol=0.001)


def test_mm_infilling_multi(infilling_database, scenarios):
    cruncher = EqualQuantileWalk_MM(infilling_database, kyoto_ghg_exclude_co2_vars)

    infilled_scenario = scenarios.to_iamdataframe()
    assert len(scenarios) == 2

    for v in kyoto_ghg_exclude_co2_vars:
        infiller = cruncher.derive_relationship(v, [LEAD], include_quantile=True)

        infilled_scenario = infilled_scenario.append(infiller(infilled_scenario))

    infilled_scenario = scmdata.ScmRun(infilled_scenario)

    # Check that the bottom up GHG is the same
    infilled_ghg = calc_ghg(infilled_scenario, kyoto_ghg_exclude_co2_vars)
    infilled_cum_ghg = infilled_ghg.values.sum(axis=1)
    scenario_cum_ghg = infilled_scenario.filter(variable=LEAD).values.sum(axis=1)

    np.testing.assert_allclose(infilled_cum_ghg, scenario_cum_ghg, rtol=0.001)
