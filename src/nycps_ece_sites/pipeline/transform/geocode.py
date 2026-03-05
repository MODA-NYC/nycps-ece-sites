# %%
import pandas as pd
import random
import os

import requests

from nycps_ece_sites.utils import config_paths

from tabulate import tabulate
import textwrap

RAW_DIR = config_paths.RAW_DATA_DIR
# %%

if __name__ == '__main__':
    year = 2025
    df = pd.read_excel(RAW_DIR / f"site_dir_{year}.xlsx")

# %% Set up data to Geocode the new data

# Set the headers with the subscription key
SUBSCRIPTION_KEY = os.getenv('NYC_API')
HEADERS = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
}

# BASE_URL = "https://api.nyc.gov/geo/geoclient/v2/address.json"
BASE_URL = "https://api.nyc.gov/geoclient/v2/address.json"

response_columns = [
    'latitude', 'longitude',
    'xCoordinate', 'yCoordinate', 
    'communityDistrict',
]
# %%'

print_output = True
rand_seed = None
sample_size = 5

# generate id variable
assert ~(df[['schooldbn', 'admission_process']].duplicated().any())
df['id'] = df['schooldbn'] + '_' + df['admission_process']

# create address df
geo_df = df[['id', 'address']].copy()

# %%

# if there are any consecutive commas in a row; if there are
# replace them with a single comma
geo_df['address'] = geo_df['address'].str.replace(r',\s*,+', ',', regex=True)

# split address by comma
geo_df[['street', 'borough', 'zip']] = geo_df['address'].str.split(',', expand=True)
for col in ['street', 'borough', 'zip']:
    geo_df[col] = geo_df[col].str.strip()

# extract house number and street name from street column
geo_df[['house_number', 'street_name']] = geo_df['street'].str.extract(r'^(\d+-?\d*[AB]?)\s+(.*)')
geo_df.drop(columns='street', inplace=True)

geo_cols = ['address', 'street', 'borough', 'zip']

# %% Borough

# Details on borough parameter
# https://mlipper.github.io/geoclient/docs/current/user-guide/#borough
# NOT case sensitive
borough_list = [
    "manhattan", "mn", "bronx", "bx", "the bronx", "brooklyn", "bk", "bklyn",
    "queens", "qn", "staten island", "si", "statenisland", "statenis",
    "new york", "new york city", "n.y.c.", "nyc", "n.y.", "ny",
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
    'st. albans': 'saint albans'
}
geo_df['borough'] = geo_df['borough'].str.lower().replace(replace_dict)

if ~(geo_df['borough'].str.lower().isin(borough_list).all()):
    # check rows that are not in 
    print('\nBoroughs not in geoclient `borough` variable:')
    check_row = ~(geo_df['borough'].str.lower().isin(borough_list))
    print_df = geo_df.loc[check_row, ['address', 'street_name', 'borough', 'zip']]
    print(tabulate(print_df, headers='keys'))
    # return

if print_output:
    print('\nBorough value counts:')
    print_df = geo_df['borough'].value_counts(dropna=False).to_frame()
    print(tabulate(print_df, headers='keys'))

# %% Zip code
# check all zip codes are formatted like "NY 11226"
assert (geo_df['zip'].str[:2] == 'NY').all()
geo_df['zip'] = geo_df['zip'].str[3:]

# check zip code is always 5 numbers
assert geo_df['zip'].str.fullmatch(r'\d{5}').all()
# %%

if print_output:
    print(f'\nRandom sample of addresses:')
    if rand_seed is None:
        rand_seed = random.randint(0, 1_000_000)
        print(f'(Random seed = {rand_seed})')
    rng = random.Random(rand_seed)
    print_df = geo_df[['address', 'house_number', 'street_name', 'borough', 'zip']].sample(sample_size, random_state=rand_seed)
    print(tabulate(print_df, headers='keys', showindex=False))

# %%

def geocode_address(row, return_all=False):
    """
    Call Geoclient v2 address endpoint.
    Borough can be full name (e.g. 'BROOKLYN') or code ('BK', 'MN', 'BX', 'QN', 'SI').
    Either borough or zip is required; providing both improves accuracy.
    """

    params = {
        "houseNumber": row['house_number'],
        "street": row['street_name'],
        "borough": row['borough'],
        "zip": row['zip'],
    }

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        address_data = data.get("address", {})
        message = address_data.get("message", None)  # Error message if any
        if return_all:
            return data
        
        # build result dynamically from response_columns
        result = {col: address_data.get(col) for col in response_columns}

        return pd.Series(result)

    except requests.exceptions.RequestException as e:
        result = {col: None for col in response_columns}
        print('Error: ')
        print(str(e))
        return pd.Series(result)


if __name__ == '__main__':
    test_df = geo_df.sample(5, random_state=2)
    print(tabulate(test_df[['house_number', 'street_name', 'borough', 'zip']], headers='keys', showindex=False))

    response = geocode_address(test_df.iloc[0], return_all=True)

    test_df[response_columns] = test_df.apply(geocode_address, axis=1)
    print_df = test_df[['house_number', 'street_name', 'borough', 'zip'] + response_columns]
    print(tabulate(print_df, headers='keys', showindex=False))

