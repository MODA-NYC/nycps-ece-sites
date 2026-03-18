# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

RAW_DIR = config_paths.RAW_DATA_DIR
# %%

def get_site_data(print_output: bool = False) -> None:
    """
    Get the site data for the specified years and save it to the raw data 
    directory.

    Source: https://infohub.nyced.org/reports/admissions-and-enrollment/directory-data
    """
    year_list = [2019, 2020, 2021, 2022, 2023, 2024, 2025]

    for year in year_list:

        get_url = (
            f"https://infohub.nyced.org/docs/default-source/default-document-library/ose"
            f"/fall-{year}---es-directory-data.xlsx"
        )

        raw_df = pd.read_excel(get_url)

        save_path = RAW_DIR / f"site_dir_{year}.xlsx"

        raw_df.to_excel(save_path, index=False)

        if print_output:
            print(f"Saved site data for year {year} to {save_path}")

# %%

if __name__ == "__main__":
    get_site_data(print_output=True)
# %%
