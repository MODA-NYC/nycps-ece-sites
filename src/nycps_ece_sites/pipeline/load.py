# %%
from pathlib import Path

import pandas as pd

_TRANSFORMED_DIR = Path(__file__).parent.parent / 'data' / 'transformed'

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

# %%

def load_sites(years):
    """
    Load transformed site data for one or more years.

    Parameters:
    - years: a single year (int) or a list of years

    Returns a DataFrame at (schooldbn, admission_process, program_code) grain.
    If multiple years are requested, returns a concatenated DataFrame.
    """
    if isinstance(years, int):
        years = [years]

    pieces = []
    for year in years:
        path = _TRANSFORMED_DIR / f'site_dir_{year}.parquet'
        df = pd.read_parquet(path)
        df['year'] = year
        pieces.append(df)

    return pd.concat(pieces, ignore_index=True)

# %%

if __name__ == '__main__':
    df = load_sites(2025)
    print(f'2025: {len(df):,} rows, {len(df.columns)} columns')

    df_multi = load_sites([2024, 2025])
    print(f'2024-2025: {len(df_multi):,} rows')
# %%
