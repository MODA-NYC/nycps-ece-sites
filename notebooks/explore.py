# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

from tabulate import tabulate
import textwrap

RAW_DIR = config_paths.RAW_DATA_DIR
# %%

year = 2025

df = pd.read_excel(RAW_DIR / f"site_dir_{year}.xlsx")

# %%

print(f"\nNumber of rows: {len(df):,}")

print(f"\nData unique by `schooldbn` and `admission_process`.")
assert ~(df[['schooldbn', 'admission_process']].duplicated().any())

print(f"\nCounts by `admission_process`:")
print_df = df['admission_process'].value_counts(dropna=False).reset_index()
print(tabulate(print_df, headers='keys', showindex=False, floatfmt=',.f'))

# %%

assert (df.groupby('schooldbn')['address'].nunique() == 1).all()

print(f"All DBNs have only one address.")

# %%

print_str = f"""In general, K sites list total students, while 
non-K sites (3K and PK) do not:
"""
print(textwrap.dedent(textwrap.fill(print_str, 80)))

name_prog_cols = ['name_prog1', 'name_prog2', 'name_prog3', 'name_prog4', 'name_prog5']
# K that do not list total students
check_row = ((df['admission_process'] == 'K') & (df['totalstudents'].isna()))
df.loc[check_row, ['schooldbn'] + name_prog_cols]

print_str = f"""
* Number of K sites that do not list total students: {check_row.sum():,}.
"""
print(textwrap.fill(print_str, 80))

check_row = ((df['admission_process'] != 'K') & (df['totalstudents'].notna()))
df.loc[check_row, ['schooldbn', 'totalstudents'] + name_prog_cols]
print_str = f"""
* Number of non-K sites that list total students: {check_row.sum():,}.
"""
print(textwrap.fill(print_str, 80))

# %%

for col in [col for col in df.columns if 'code_prog' in col]:
    assert ((df[col].str[:6] == df['schooldbn']) | (df[col].isna())).all()

print("All `code_prog` columns start with the `schooldbn` value or are NA.")

# %%
