# %%
import pandas as pd
import pytest


@pytest.fixture
def raw_site_df():
    """Minimal raw site directory DataFrame, mimicking the xlsx structure."""
    return pd.DataFrame({
        'schooldbn': ['01M001', '02K002', '08G778', '24Q019'],
        'admission_process': ['PK', '3K', 'PK', 'K'],
        'address': [
            '100 MAIN STREET, MANHATTAN, NY 10001',
            '200 FLATBUSH AVENUE, BROOKLYN, NY 11217',
            '300 GRAND CONCOURSE, BRONX, NY 10451',
            '400 QUEENS BLVD, QUEENS, NY 11368',
        ],
    })


@pytest.fixture
def formatted_geo_df():
    """Minimal geo DataFrame mimicking the output of _00_set_up_geocode_df.

    Borough is UPPERCASE (as split from the address string);
    zip is still in 'NY XXXXX' format (before _02_format_zip strips it).
    """
    return pd.DataFrame({
        'id': ['01M001', '02K002', '08G778', '24Q019'],
        'address': [
            '100 MAIN STREET, MANHATTAN, NY 10001',
            '200 FLATBUSH AVENUE, BROOKLYN, NY 11217',
            '300 GRAND CONCOURSE, BRONX, NY 10451',
            '400 QUEENS BLVD, QUEENS, NY 11368',
        ],
        'borough': ['MANHATTAN', 'BROOKLYN', 'BRONX', 'QUEENS'],
        'zip': ['NY 10001', 'NY 11217', 'NY 10451', 'NY 11368'],
        'house_number': ['100', '200', '300', '400'],
        'street_name': ['MAIN STREET', 'FLATBUSH AVENUE', 'GRAND CONCOURSE', 'QUEENS BLVD'],
    })

# %%
