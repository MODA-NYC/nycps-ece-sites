# %%

from nycps_ece_sites.pipeline.extract import get_site_data

# %%
def main():
    # extract site data (will save files to data/raw/)
    print('Extracting site data...')
    get_site_data(print_output=True)

if __name__ == '__main__':
    main()
# %%
