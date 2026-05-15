# %%
import pandas as pd

from nycps_ece_sites.pipeline.transform.geocode import (
    _00_set_up_geocode_df,
    _01_replace_borough,
    _02_format_zip,
    replace_address,
)

EXPECTED_GEO_COLUMNS = {'id', 'address', 'borough', 'zip', 'house_number', 'street_name'}


def test_set_up_geocode_df_columns(raw_site_df):
    result = _00_set_up_geocode_df(raw_site_df)
    assert set(result.columns) == EXPECTED_GEO_COLUMNS


def test_set_up_geocode_df_no_duplicate_ids(raw_site_df):
    result = _00_set_up_geocode_df(raw_site_df)
    assert not result['id'].duplicated().any()


def test_replace_borough_all_valid(formatted_geo_df):
    # borough_list is defined inside _01_replace_borough; check fixture values directly
    expected = {'manhattan', 'brooklyn', 'bronx', 'queens'}
    result = _01_replace_borough(formatted_geo_df)
    assert set(result['borough'].str.lower().unique()) == expected


def test_format_zip_five_digits(formatted_geo_df):
    result = _02_format_zip(formatted_geo_df)
    assert result['zip'].str.fullmatch(r'\d{5}').all()


def test_replace_address_applies_correction():
    df = pd.DataFrame({
        'id': ['17KBSP'],
        'address': ['771 CROWN STREET, NEW YORK, NY 11213'],
    })
    correction = {
        '17KBSP': {
            '771 CROWN STREET, NEW YORK, NY 11213':
            '771 CROWN STREET, BROOKLYN, NY 11213'
        }
    }
    result = replace_address(df, replace_dict=correction)
    assert result.loc[result['id'] == '17KBSP', 'address'].iloc[0] == (
        '771 CROWN STREET, BROOKLYN, NY 11213'
    )

# %%
