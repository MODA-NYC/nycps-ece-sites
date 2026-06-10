# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

GEOCODE_DIR = config_paths.GEOCODE_DIR
RAW_DIR = config_paths.RAW_DATA_DIR

GEO_COLS = [
    'schooldbn', 'borough', 'zip', 'house_number', 'street_name',
    'latitude', 'longitude', 'xCoordinate', 'yCoordinate', 'communityDistrict',
]


def merge_geo(year, print_output=False):
    """
    Merge geocoded data for a given year onto a site directory dataframe.

    Parameters:
    - df: site directory dataframe with a `schooldbn` column
    - year: year of the geocoded data to load (e.g. 2025)
    - print_output: whether to print progress

    Returns:
    - merged dataframe with geo columns added
    """
    if print_output:
        print(f'\nMerging geocoded data for {year} onto site dataframe.')

    raw_df = pd.read_excel(RAW_DIR / f'site_dir_{year}.xlsx')
    # Assumes you've already geocoded data
    geo_df = pd.read_csv(GEOCODE_DIR / f'site_dir_geo_{year}.csv', usecols=GEO_COLS)

    merge_df = pd.merge(
        left=raw_df,
        right=geo_df,
        on='schooldbn',
        how='left',
        validate='m:1',
    )

    if print_output:
        n_in = len(raw_df)
        n_out = len(merge_df)
        n_matched = merge_df['latitude'].notna().sum()
        print(f'  Rows in: {n_in}, rows out: {n_out}')
        print(f'  Sites with latitude: {n_matched}/{n_out}')

    return merge_df


# %%

if __name__ == '__main__':
    merge_geo('2019', print_output=True)

# %%
