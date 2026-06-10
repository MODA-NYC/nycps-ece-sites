# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

RAW_DIR = config_paths.RAW_DATA_DIR

year = 2024
raw_df = pd.read_excel(RAW_DIR / f'site_dir_{year}.xlsx')

priority_cols = raw_df.columns[raw_df.columns.str.contains('priority')]

# droppping the 114 admission priority columns
raw_df.drop(columns = priority_cols, inplace=True)


# %%
