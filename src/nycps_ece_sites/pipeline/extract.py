# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

RAW_DIR = config_paths.RAW_DATA_DIR
# %%

def get_site_data():
    """
    Get the site data for the specified years and save it to the raw data 
    directory.
    """
    year_list = [2025]

    for year in year_list:

        get_url = (
            f"https://infohub.nyced.org/docs/default-source/default-document-library/ose"
            f"/fall-{year}---es-directory-data.xlsx"
        )

        raw_df = pd.read_excel(get_url)

        save_path = RAW_DIR / f"site_dir_{year}.xlsx"

        raw_df.to_excel(save_path, index=False)

        print(f"Saved site data for year {year} to {save_path}")

# %%

if __name__ == "__main__":
    get_site_data()
# %%
