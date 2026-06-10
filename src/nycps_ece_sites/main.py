# %%

from nycps_ece_sites.pipeline.extract import get_site_data
from nycps_ece_sites.pipeline.transform.main import transform_site_data

# %%
def main():
    """
    Run the full pipeline: extract site data, then transform.

    Geocoding is not run here — it is a slow, manual step. Run
    geocode.py for each year before running this if geocoded files
    are missing or out of date.
    """
    print('Extracting site data...')
    get_site_data(print_output=True)

    print('\nNote: geocoding is not run by default. Run geocode.py manually if geocoded files are missing or out of date.')
    print('\nTransforming site data...')
    transform_site_data(print_output=True)

if __name__ == '__main__':
    main()
# %%
