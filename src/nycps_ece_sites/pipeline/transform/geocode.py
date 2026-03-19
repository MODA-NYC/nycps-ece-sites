# %%
import pandas as pd
import random
import os
import time

import requests
import truststore
truststore.inject_into_ssl()
from dotenv import load_dotenv

from nycps_ece_sites.utils import config_paths

from tabulate import tabulate
import textwrap

RAW_DIR = config_paths.RAW_DATA_DIR
GEOCODE_DIR = config_paths.GEOCODE_DIR
ROOT_DIR = config_paths.ROOT_DIR

# Load .env from project root
load_dotenv(ROOT_DIR / '.env')
# %%

if __name__ == '__main__':
    # year = 2025
    year = 2024
    df = pd.read_excel(RAW_DIR / f"site_dir_{year}.xlsx")

# %% Set up data to Geocode the new data

# Set the headers with the subscription key
def _get_headers():
    key = os.getenv('NYC_API')
    if key is None:
        raise ValueError("NYC_API environment variable is not set")
    return {
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': key,
    }

# BASE_URL = "https://api.nyc.gov/geo/geoclient/v2/address.json"
BASE_URL = "https://api.nyc.gov/geoclient/v2/address.json"

response_columns = [
    'latitude', 'longitude',
    'xCoordinate', 'yCoordinate', 
    'communityDistrict',
]
# %%'

RUN_ALL = False
CHECK_ALL = False
RUN_TEST_ONLY = True
print_output = True
rand_seed = None
sample_size = 5

# address replace; if there are any incorrect addresses, replace them here
replace_address_dict_2025 = {
    # {site : {old_address: new_address}}
    '08G778' : {
        '2108 LACOMBE AVENUE, BROOKLYN, NY 10473': 
        '2108 LACOMBE AVENUE, BRONX, NY 10473'
    },
    '17KBSP' : {
        '771 CROWN STREET, NEW YORK, NY 11213':
        '771 CROWN STREET, BROOKLYN, NY 11213'
    },
    '24Q019' : {
        '44-10 99 Street, Queens, NY 11368':
        '40-10 99 Street, Queens, NY 11368'
    },
    '24Z123' : {
        '54-25 101 STREET, NEW YORK, NY 11368':
        '54-25 101st STREET, QUEENS, NY 11368'
    },
    '24Z124': {
        '104-04 CORONA AVENUE, NEW YORK, NY 11368':
        '104-04 CORONA AVENUE, QUEENS, NY 11368'
    },
    '24Z125': {
        '108-18 ROOSEVELT AVENUE, NEW YORK, NY 11368':
        '108-18 ROOSEVELT AVENUE, QUEENS, NY 11368'
    },	
    '25H112' : {
        '14 121ST STREET, QUEENS, NY 11356':
        '14-24 121ST STREET, QUEENS, NY 11356'
    },
    '26QAJX' : {
        '238-10 HILLSIDE AVENUE BELLEROSE, QUEENS, NY 11427':
        '238-10 HILLSIDE AVENUE, QUEENS, NY 11427'
    },
    '26QBCR' : {
        '86-29 COMMONWEATH BOULEVARD, ,BELLEROSE, NY 11426':
        '86-29 COMMONWEALTH BOULEVARD, QUEENS, NY 11426'
    },
    '27H097': {
        '149 RALEIGH STREET, QUEENS, NY 11417':
        '149-44 RALEIGH STREET, QUEENS, NY 11417'
    },
    '27H110': {
        '132 158TH STREET , QUEENS, NY 11434':
        '132-31 158TH STREET, QUEENS, NY 11434'
    },
    '28G999': {
        '102-35 63 ROAD DR, QUEENS, NY 11375':
        '102-35 63 RD, QUEENS, NY 11375'
    },
    '29QAXD': {
        '10960 202ND STREET, ST. ALBANS, NY 11412':
        '109-60 202ND STREET, Queens, NY 11412'
    },
    '29QAXQ': {
        '90-04 175TH STEET, QUEENS, NY 11432':
        '90-04 175TH STREET, QUEENS, NY 11432'
    },
    '30H100': {
        '31 34TH STREET, QUEENS, NY 11106':
        '31-14 34TH STREET, QUEENS, NY 11106'
    },
    '31G917': {
        '46 B CIRCLE LOOP, STATEN ISLAND, NY 10304':
        '46B CIRCLE LOOP, STATEN ISLAND, NY 10304'
    },
    '31RAKL': {
        '471 NORTH GANNON AVENUE STATEN ISLAND NEW YORK 10314, STATEN ISLAND, NY 10314':
        '471 NORTH GANNON AVENUE, STATEN ISLAND, NY 10314'
    }
}

replace_address_dict_2024 = {
    '05MAWW': {
        '3333 BROADWAY, MANHATTAN, NY 10031':
        '3301 BROADWAY, MANHATTAN, NY 10031'
    },
    '08G778' : {
        '2108 LACOMBE AVENUE, BROOKLYN, NY 10473': 
        '2108 LACOMBE AVENUE, BRONX, NY 10473'
    },
    '17KBSP' : {
        '771 CROWN STREET, NEW YORK, NY 11213':
        '771 CROWN STREET, BROOKLYN, NY 11213'
    },
    '24Z123' : {
        '54-25 101 STREET, NEW YORK, NY 11368':
        '54-25 101st STREET, QUEENS, NY 11368'
    },
    '24Z125': {
        '108-18 ROOSEVELT AVENUE, NEW YORK, NY 11368':
        '108-18 ROOSEVELT AVENUE, QUEENS, NY 11368'
    },
    '26QAJX' : {
        '238-10 HILLSIDE AVENUE BELLEROSE, QUEENS, NY 11427':
        '238-10 HILLSIDE AVENUE, QUEENS, NY 11427'
    },
    '26QBCR' : {
        '86-29 COMMONWEATH BOULEVARD, ,BELLEROSE, NY 11426':
        '86-29 COMMONWEALTH BOULEVARD, QUEENS, NY 11426'
    },
    '29QAXD': {
        '10960 202ND STREET, ST. ALBANS, NY 11412':
        '109-60 202ND STREET, Queens, NY 11412'
    },
    '29QAXQ': {
        '90-04 175TH STEET, QUEENS, NY 11432':
        '90-04 175TH STREET, QUEENS, NY 11432'
    },
    '31RAKL': {
        '471 NORTH GANNON AVENUE STATEN ISLAND NEW YORK 10314, STATEN ISLAND, NY 10314':
        '471 NORTH GANNON AVENUE, STATEN ISLAND, NY 10314'
    }
}

# lookup: year -> address replacement dict
REPLACE_ADDRESS_DICTS = {
    2025: replace_address_dict_2025,
    2024: replace_address_dict_2024,
    2023: {},
    2022: {},
    2021: {},
    2020: {},
    2019: {},
    # add future years here, e.g.:
    # 2026: replace_address_dict_2026,
}

def replace_address(df, replace_dict, id_var='id', print_output=False):
    df = df.copy()
    for site, address in replace_dict.items():
        for old_address, new_address in address.items():
            replace_row = ((df[id_var] == site) & (df['address'] == old_address))
            if replace_row.any():
                df.loc[replace_row, 'address'] = new_address
                if print_output:
                    print_str = (
                        f'Replaced address for site {site}:\n'
                        f'Old address: {old_address}\n'
                        f'New address: {df.loc[replace_row, "address"].values[0]}\n'
                    )
                    print(print_str)

    return df


if __name__ == '__main__':
    df_copy = df.copy()
    df_copy = replace_address(
        df=df_copy, replace_dict=REPLACE_ADDRESS_DICTS.get(year, {}), 
        id_var='schooldbn', print_output=True)

# %%
## SET UP
# Make ID, 

def _00_set_up_geocode_df(df, id_var=['schooldbn'], replace_address_dict={}, print_output=False):
    """
    Creates a geo dataframe with columns for house number, street name, borough, and zip code

    Parameters:
    - df: original dataframe with address column
    - id_var: variable(s) to use as unique identifier for each row; if using more
    - replace_address_dict: dictionary to replace address

    Notes:
    * Returns a dataframe with `id`, `address`, and columns built from address
      (house number, street_name, borough, and zip)
    * Will join multiple id columns if necessary. Note this for merging in dataframes
      in the future. 
    """
    df = df.copy()
    if print_output:
        print_str = (
            "\nSTEP 0: Setting up geo dataframe for geocoding. "
        )
        print(print_str)

    if print_output:
        print_str = (
            "A. Creating a geo dataframe with `id` and `address`."
        )
        print(textwrap.fill(print_str, 80))
    # if using more than one variable, combine them to create a unique id
    df['id'] = df[id_var].agg('_'.join, axis=1)

    # create address df
    geo_df = df[['id', 'address']].copy()

    # if there are any consecutive commas in a row; if there are
    # replace them with a single comma
    if print_output:
        print_str = (
            "B. Format address; replace values if necessary.\n"
        )
        print(print_str)

    # replace any addresses, if necessary
    if len(replace_address_dict) > 0:
        geo_df = replace_address(
            geo_df, replace_dict=replace_address_dict, 
            id_var='id', print_output=print_output
        )
    
    # remove any consecutive commas in the address; this can cause issues with geocoding
    geo_df['address'] = geo_df['address'].str.replace(r',\s*,+', ',', regex=True)


    # drop duplicates
    if print_output:
        print_str = (
            "C. Dropping duplicates from geo dataframe."
        )
        print(print_str)
    geo_df = geo_df.drop_duplicates()
    
    # split address by comma
    if print_output:
        print_str = (
            "D. Splitting address into street, borough, and zip."
        )
        print(print_str)
    geo_df[['street', 'borough', 'zip']] = geo_df['address'].str.split(',', expand=True)
    for col in ['street', 'borough', 'zip']:
        geo_df[col] = geo_df[col].str.strip()

    # extract house number and street name from street column
    geo_df[['house_number', 'street_name']] = geo_df['street'].str.extract(r'^(\d+-?\d*[AB]?)\s+(.*)')
    geo_df.drop(columns='street', inplace=True)

    # geo_cols = ['address', 'street', 'borough', 'zip']

    return geo_df

if __name__ == '__main__':
    geo_df = _00_set_up_geocode_df(
        df, print_output=True,
        replace_address_dict=REPLACE_ADDRESS_DICTS.get(year, {}))

# %%

def _01_replace_borough(geo_df, print_output=False):
    if print_output:
        print_str = (
            "\nSTEP 1: Replacing borough values to match geoclient `borough` variable."
        )
        print(print_str)
    # Details on borough parameter
    # https://mlipper.github.io/geoclient/docs/current/user-guide/#borough
    # NOT case sensitive
    borough_list = [
        "manhattan", "mn", "bronx", "bx", "the bronx", "brooklyn", "bk", "bklyn",
        "queens", "qn", "staten island", "si", "statenisland", "statenis",
        # "new york",   # although 'new york' was in the list, geoclient didn't return results
        "new york city", "n.y.c.", "nyc", "n.y.", "ny",
        "arverne", "astoria", "bayside", "bellerose", "breezy point",
        "cambria heights", "college point", "corona", "east elmhurst", "elmhurst",
        "far rockaway", "floral park", "flushing", "forest hills",
        "fresh meadows", "glen oaks", "hollis", "howard beach", "inwood",
        "jackson heights", "jamaica", "kew gardens", "little neck",
        "long island city", "maspeth", "middle village", "new hyde park",
        "oakland gardens", "ozone park", "qs", "queens village", "rego park",
        "richmond hill", "ridgewood", "rockaway park", "rosedale",
        "saint albans", "south ozone park", "south richmond hill",
        "springfield gardens", "sunnyside", "whitestone", "woodhaven",
        "woodside"
    ]

    # fix miscellaneous errors; these don't properly match
    replace_dict = {
        'staten is': 'staten island',
        'st. albans': 'saint albans',
        'saint albans': 'saint albans',
        'new york': 'manhattan',
        'new york city': 'manhattan',
        'ny': 'manhattan',
        'jamaica': 'queens', 
        'flushing': 'queens', 
        'astoria': 'queens', 
        'middle village': 'queens', 
        'ridgewood': 'queens', 
        'elmhurst': 'queens', 
        'long island city': 'queens',
        'east elmhurst': 'queens', 
        'maspeth': 'queens', 
        'bayside': 'queens', 
        'bellerose': 'queens',
        'south ozone park': 'queens', 
        'howard beach': 'queens', 
        'richmond hill': 'queens', 
        'kew gardens': 'queens',
        'saint albans': 'queens', 
        'springfield gardens': 'queens', 
        'queens village': 'queens',
        'rockaway park': 'queens',
    }
    geo_df['borough'] = geo_df['borough'].str.lower().replace(replace_dict)

    if ~(geo_df['borough'].str.lower().isin(borough_list).all()):
        # check rows that are not in geoclient `borough` variable
        print('\nBoroughs not in geoclient `borough` variable:')
        check_row = ~(geo_df['borough'].str.lower().isin(borough_list))
        print_df = geo_df.loc[check_row, ['address', 'street_name', 'borough', 'zip']]
        print(tabulate(print_df, headers='keys'))
        # return

    if print_output:
        print('\nBorough value counts:')
        print_df = geo_df['borough'].value_counts(dropna=False).to_frame()
        print(tabulate(print_df, headers='keys'))

    return geo_df

if __name__ == '__main__':
    geo_df = _01_replace_borough(geo_df, print_output=True)

# %% Zip code

def _02_format_zip(geo_df, print_output=False):
    if print_output:
        print_str = (
            "\nSTEP 2: Formatting zip code to match geoclient `zip` variable."
        )
        print(print_str)
    # check all zip codes are formatted like "NY 11226"
    assert (geo_df['zip'].str[:2] == 'NY').all()
    geo_df['zip'] = geo_df['zip'].str[3:]

    # check zip code is always 5 numbers
    assert geo_df['zip'].str.fullmatch(r'\d{5}').all()
    return geo_df

if __name__ == '__main__':
    geo_df = _02_format_zip(geo_df, print_output=True)


# %%

def _format_df(
        df, print_output=False, replace_address_dict=None,
        id_var='schooldbn'
    ):
    """
    Format dataframe for geocoding
    """
    if replace_address_dict is None:
        replace_address_dict = {}

    if print_output:
        print_str = (
            "\nFormatting dataframe for geocoding."
        )
        print(print_str)
    geo_df = _00_set_up_geocode_df(
        df, replace_address_dict=replace_address_dict, 
        print_output=print_output, id_var=[id_var])
    geo_df = _01_replace_borough(geo_df, print_output=print_output)
    geo_df = _02_format_zip(geo_df, print_output=print_output)
    return geo_df

if __name__ == '__main__':
    geo_df = _format_df(df, print_output=True, replace_address_dict=REPLACE_ADDRESS_DICTS.get(year, {}))


# %% Random sample of addresses

def check_address_fmt(geo_df, rand_seed=None, sample_size=5):
    """
    Generates a random sample of addresses to check format variables. By changing 
    the seed and sample size, you can see if the address looks reasonable, 
    and that house_number, street_name, borough, and zip all look correct
    """
    print(f'\nRandom sample of addresses:')
    if rand_seed is None:
        rand_seed = random.randint(0, 1_000_000)
        print(f'(Random seed = {rand_seed})')
    rng = random.Random(rand_seed)
    print_df = geo_df[['id', 'address', 'house_number', 'street_name', 'borough', 'zip']].sample(sample_size, random_state=rand_seed)
    print(tabulate(print_df, headers='keys', showindex=False))

if __name__ == '__main__':
    check_address_fmt(geo_df, rand_seed=2, sample_size=5)

# %%

def geocode_address(row, return_all=False, print_errors=False):
    """
    Call Geoclient v2 address endpoint.
    Borough can be full name (e.g. 'BROOKLYN') or code ('BK', 'MN', 'BX', 'QN', 'SI').
    Either borough or zip is required; providing both improves accuracy.

    If print_errors is True, will print any error messages returned by the API 
    for debugging purposes.
    """

    params = {
        "houseNumber": row['house_number'],
        "street": row['street_name'],
        "borough": row['borough'],
        "zip": row['zip'],
    }

    try:
        response = requests.get(BASE_URL, headers=_get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        address_data = data.get("address", {})
        message = address_data.get("message", None)  # Error message if any
        if message is not None:
            if print_errors:
                print(f"Geocoding error for address '{row['address']}': {message}")
            # result = {col: None for col in response_columns}
            # return pd.Series(result)
        if return_all:
            return data
        
        # build result dynamically from response_columns
        result = {col: address_data.get(col) for col in response_columns}

        return pd.Series(result)

    except requests.exceptions.RequestException as e:
        result = {col: None for col in response_columns}
        if print_errors:
            print(f"Geocoding request error for address '{row['address']}': {str(e)}")
        return pd.Series(result)

if __name__ == '__main__':
    test_df = geo_df.sample(5, random_state=2)
    print(tabulate(test_df[['house_number', 'street_name', 'borough', 'zip']], headers='keys', showindex=False))

    response = geocode_address(test_df.iloc[0], return_all=True)

    test_df[response_columns] = test_df.apply(geocode_address, axis=1, print_errors=True)
    print_df = test_df[['house_number', 'street_name', 'borough', 'zip'] + response_columns]
    print(tabulate(print_df, headers='keys', showindex=False))


# %%
def geocode_df(df, print_errors=False, response_columns=response_columns):
    """
    Geocode a dataframe of addresses using the Geoclient API.

    Parameters:
    - df: dataframe with columns for house_number, street_name, borough, and zip
    - print_errors: if True, will print any error messages returned by the API for debugging
    - response_columns: list of columns to include in the geocoded dataframe

    Returns:
    - df: dataframe with geocoded address information
    """
    df[response_columns] = df.apply(geocode_address, axis=1, print_errors=print_errors)
    return df

def print_geocode_df(df, sample_size=5, random_state=None):
    print_df = df.sample(sample_size, random_state=random_state)

    print(tabulate(print_df[['house_number', 'street_name', 'borough', 'zip'] + response_columns], headers='keys', showindex=False))

if __name__ == '__main__':
    test_df = geo_df.sample(5, random_state=2)
    test_df = geocode_df(test_df)

    print_geocode_df(test_df)


# %% Run everything
if __name__ == '__main__':
    if RUN_ALL:
        geo_df = geocode_df(geo_df)

# %%

if __name__ == '__main__':

    # find missing geocodes
    if CHECK_ALL: 
        check_df = geo_df.loc[geo_df['latitude'].isna()].copy()
        check_df = geo_df.loc[geo_df['latitude'].isna()]



# %% When refreshing address replace dict, start here

if __name__ == '__main__':

    if CHECK_ALL: 
        if len(check_df) > 0:
            check_df = replace_address(
                df=check_df, id_var='id', 
                replace_dict=REPLACE_ADDRESS_DICTS.get(year, {}), print_output=True)

            check_df = _00_set_up_geocode_df(check_df, id_var=['id'])
            check_df = _01_replace_borough(check_df, print_output=True)
            check_df = _02_format_zip(check_df, print_output=True)
            check_df = geocode_df(check_df, print_errors=True)

# %%
if __name__ == '__main__':
    if CHECK_ALL:
        # repeat the process
        if len(check_df) > 0:
            check_df = check_df.loc[check_df['latitude'].isna()]
            check_df.drop(columns=response_columns, inplace=True)
            check_df = geocode_df(check_df, print_errors=True)
# %%

if __name__ == '__main__':
    if CHECK_ALL:
        if len(check_df) > 0:
            # try and debug individual addr esses
            check_row = check_df.iloc[0]
            # check_row = check_df.loc[167]
            param_check = {
                'houseNumber': check_row['house_number'], 'street': check_row['street_name'], 
                'borough': check_row['borough'], 'zip': check_row['zip']
            }
            # param_check = {
            #     'houseNumber': '3301', 'street': 'BROADWAY', 
            #     'borough': 'manhattan', 'zip': '10031'  
            # }
            response = requests.get(
                BASE_URL, headers=_get_headers(), params=param_check, timeout=10)
            for key, value in response.json()['address'].items():
                print(f'{key}: {value}')


            # df.loc[df['schooldbn'] == '17KBSP', ['address', 'url']]
            # df.loc[df['schooldbn'] == '24Q019', ['address', 'url']]
            # df.loc[df['schooldbn'] == '24Z123', ['address', 'url']]
            # df.loc[df['schooldbn'] == '24Z125', ['address', 'url']]
            # df.loc[df['schooldbn'] == '26QAJX', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '26QBCR', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '27H097', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '27H110', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '28G999', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '29QAXD', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '29QAXQ', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '30H100', ['schooldbn', 'address', 'url']]
            # df.loc[df['schooldbn'] == '05MAWW', ['schooldbn', 'address', 'url']]
            df.loc[df['schooldbn'] == '08G778', ['schooldbn', 'address', 'url']]


# %%

def geocode_site_data(
        df, id_var='schooldbn', replace_address_dict=None,
        print_output=False, save_path=None
    ):
    """
    Format and geocode a site directory dataframe.

    Parameters:
    - df: raw site directory dataframe
    - id_var: column to use as unique site identifier
    - replace_address_dict: dict of address corrections (keyed by site id)
    - print_output: whether to print progress
    - save_path: if provided, save the geocoded dataframe to this path

    Returns:
    - geo_df: geocoded dataframe with id, address, and geocode columns
    """
    geo_df = _format_df(
        df, print_output=print_output,
        id_var=id_var, replace_address_dict=replace_address_dict)

    if print_output:
        print('\nGeocoding addresses...')
    geo_df = geocode_df(geo_df, print_errors=False)

    # rename variable for merging back into original site directory dataframe
    geo_df.rename(columns={'id': 'schooldbn'}, inplace=True)

    if save_path is not None:
        geo_df.to_csv(save_path, index=False)
        if print_output:
            print(f"\nSaved geocoded data to {save_path}")

    return geo_df


def merge_geocode(df, geo_df, id_var='schooldbn'):
    """
    Merge geocoded data back onto the original site directory dataframe.

    Parameters:
    - df: original site directory dataframe; contains id_var `schooldbn`
    - id_var: column used as unique site identifier in original site df
    - geo_df: geocoded dataframe (output of geocode_site_data; contains `id`)

    Returns:
    - merge_df: merged dataframe
    """
    merge_df = pd.merge(
        left=df,
        right=geo_df,
        left_on=id_var,
        right_on=id_var,
        how='outer',
        validate='m:1',
        indicator=True
    )

    assert (merge_df['_merge'] == 'both').all()
    merge_df.drop(columns=['_merge'], inplace=True)

    return merge_df


if __name__ == '__main__':
    if RUN_TEST_ONLY:
        test_df = df.sample(5, random_state=2)
        test_geo_df = geocode_site_data(
            test_df, replace_address_dict=REPLACE_ADDRESS_DICTS.get(year, {}), print_output=True,
            # save_path=GEOCODE_DIR / f'site_dir_geo_{year}.csv'
        )
    else:
        geo_df = geocode_site_data(
            df, replace_address_dict=REPLACE_ADDRESS_DICTS.get(year, {}), print_output=True,
            save_path=GEOCODE_DIR / f'site_dir_geo_{year}.csv')
    

    # %%

if __name__ == '__main__':
    if RUN_TEST_ONLY:
        merge_df = merge_geocode(test_df, test_geo_df)
    else:
        merge_df = merge_geocode(df, geo_df)

# %%
