# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths
from nycps_ece_sites.pipeline.transform.merge_geo import merge_geo
from nycps_ece_sites.pipeline.transform.program_code_reshape import reshape_by_program_code

TRANSFORMED_DIR = config_paths.TRANSFORMED_DIR

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

# %%

def transform_site_data(years=None, print_output=False):
    """
    Merge geocoded data and reshape to long format for each year.

    Reads raw xlsx and geocoded CSVs from data/raw/ and data/geocode/.
    Writes one parquet file per year to data/transformed/.

    Parameters:
    - years: list of years to process; defaults to all years
    - print_output: whether to print progress
    """
    if years is None:
        years = YEARS

    TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)

    for year in years:
        if print_output:
            print(f'\nTransforming data for {year}...')

        merged_df = merge_geo(year, print_output=print_output)
        long_df = reshape_by_program_code(merged_df, print_output=print_output)

        # Merge site-level columns back onto the reshaped long data
        site_cols = merged_df.columns[~merged_df.columns.str.contains('_prog')]
        long_df = pd.merge(
            long_df,
            merged_df[site_cols],
            on=['schooldbn', 'admission_process'],
            how='left',
            validate='m:1',
        )

        save_path = TRANSFORMED_DIR / f'site_dir_{year}.parquet'
        long_df.to_parquet(save_path, index=False)

        if print_output:
            print(f'  Saved to {save_path}')

# %%

if __name__ == '__main__':
    transform_site_data(print_output=True)
# %%
