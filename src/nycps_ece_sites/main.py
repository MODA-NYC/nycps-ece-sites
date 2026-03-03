# %%

from nycps_ece_sites.pipeline.extract import get_site_data

# %%
def main():
    # extract site data (will save files to data/raw/)
    get_site_data(print_output=False)

if __name__ == '__main__':
    main()
# %%
