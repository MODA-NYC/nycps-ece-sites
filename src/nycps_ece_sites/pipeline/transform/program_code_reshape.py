# %%
import pandas as pd

from nycps_ece_sites.utils import config_paths

RAW_DIR = config_paths.RAW_DATA_DIR

def reshape_by_program_code(df, print_output=False):
    """Reshape raw site data from wide (by schooldbn + admissions_process) to long (by program code).

    Each input row has up to 7 program codes in code_prog1–code_prog7, with parallel
    _progN columns (e.g. admissionsmethod_prog1–admissionsmethod_prog7). Output has one
    row per (schooldbn, admissions_process, program_code), with _progN suffix stripped.
    Rows where code_progN is null are dropped.
    """
    id_cols = ['schooldbn', 'admission_process']
    prog_suffixes = [f'_prog{n}' for n in range(1, 8)]

    # Find all variable stubs that have at least one _progN column, excluding 'code'
    # (code_progN becomes the program_code identifier, not a data column)
    stubs = set()
    for col in df.columns:
        for s in prog_suffixes:
            if col.endswith(s):
                stub = col[: -len(s)]
                if stub != 'code':
                    stubs.add(stub)
                break

    pieces = []
    for n in range(1, 8):
        suffix = f'_prog{n}'
        code_col = f'code_prog{n}'

        # Rename map contains entries like the following for program code 1:
        # admissionsmethod_prog1: admissionsmethod
        # priority4_prog1: priority4
        rename_map = {
            f'{stub}{suffix}': stub
            for stub in stubs
            if f'{stub}{suffix}' in df.columns
        }
        
        # all of the program code 1 columns
        subset = df[id_cols + [code_col] + list(rename_map.keys())].copy()
        # rename the columns
        subset = subset.rename(columns={code_col: 'program_code', **rename_map})
        # drop if the program code is NAN
        subset = subset.dropna(subset=['program_code'])
        # append subset of data to list
        pieces.append(subset)

    result = pd.concat(pieces, ignore_index=True)

    if print_output:
        print(f'Reshaped to {len(result):,} rows by program code')

    return result


if __name__ == '__main__':
    year = 2025
    raw_df = pd.read_excel(RAW_DIR / f'site_dir_{year}.xlsx')
    long_df = reshape_by_program_code(raw_df, print_output=True)
    print(long_df.head())
    print(long_df.dtypes)

# %%
