# Claude Code Guidance: nycps-ece-sites

## Project overview

This repository generates and processes data on NYCPS Early Childhood Education (ECE) sites. It pulls site directory data from InfoHub, geocodes addresses via the NYC GeoClient API, and produces clean datasets for downstream use in a separate, private demand-forecasting repository.

The forecasting repo will install this package as a git dependency (`uv add git+https://github.com/MODA-NYC/nycps-ece-sites.git`), so everything here must work as a proper installable Python package.

## How to work with me

- **Go slowly. One step at a time.** Do not combine multiple changes into a single step.
- **Always check with me before proceeding.** Propose what you plan to do, wait for my approval, then do it. No exceptions.
- **Parsimony is key.** Write the minimum code needed. Do not add features, utilities, or abstractions I haven't asked for.
- **Do not refactor existing code unless I ask you to.** If you see something you'd like to clean up, mention it and wait for my go-ahead.
- **When you're unsure about a design choice, ask.** Don't guess.

## Repository structure

```
nycps-ece-sites/
├── pyproject.toml              # Package config (uv + uv_build)
├── uv.lock
├── .python-version             # Python 3.11+
├── .env                        # NYC GeoClient API key (gitignored)
├── README.md
├── data/
│   ├── raw/                    # Site directory xlsx files (2019-2025)
│   ├── geocode/                # Geocoded CSVs (2019-2025)
│   └── transformed/            # Transformed parquet files (2019-2025)
├── notebooks/
│   └── explore.py              # Interactive exploration script
├── src/nycps_ece_sites/
│   ├── __init__.py             # Exports main() and load_sites()
│   ├── main.py                 # CLI entry point; calls extract then transform (geocoding excluded)
│   ├── pipeline/
│   │   ├── extract.py          # Downloads site directory xlsx from InfoHub
│   │   ├── load.py             # load_sites(years): returns transformed DataFrame for one or more years
│   │   └── transform/
│   │       ├── main.py         # Coordinates merge_geo + reshape; writes to src/.../data/transformed/
│   │       ├── geocode.py      # Address correction + NYC GeoClient geocoding (run manually)
│   │       ├── merge_geo.py    # Merges geocoded CSVs onto raw site data on schooldbn
│   │       └── program_code_reshape.py  # Reshapes wide program codes to long format
│   └── utils/
│       └── config_paths.py     # Project root detection + path constants (RAW_DATA_DIR, GEOCODE_DIR, TRANSFORMED_DIR)
└── tests/
    ├── conftest.py              # Fixtures: raw_site_df, formatted_geo_df
    └── test_geocode_format.py  # Geocode formatting function tests
```

## Data overview

**Raw site directories** (`data/raw/site_dir_{year}.xlsx`): One file per year (2019-2025). Each row is a site × admission_process combination. Key identifiers: `schooldbn` (site ID), `admission_process` (3K, PK, or K). 167 columns in recent years, 122 columns are stable across all years. Contains address, program-level admissions info (seats, apps, priorities for up to 7 programs), and site metadata.

**Geocoded data** (`data/geocode/site_dir_geo_{year}.csv`): Produced by the geocode pipeline. Columns: `schooldbn`, `address`, `borough`, `zip`, `house_number`, `street_name`, `latitude`, `longitude`, `xCoordinate`, `yCoordinate`, `communityDistrict`. One row per unique address (deduplicated from the raw data, which can have multiple rows per schooldbn due to admission_process).

**Transformed data** (`src/nycps_ece_sites/data/transformed/site_dir_{year}.parquet`): Produced by `transform/main.py`. Bundled with the package so the forecasting repo can access it after `uv add git+...`. One row per `(schooldbn, admission_process, program_code)`. Contains all non-prog site columns (including geo) merged back in after reshape. Column counts by year: 2019 (56), 2020 (56), 2021 (55), 2022 (47), 2023–2025 (51). `communityDistrict` is int64 in years with complete geocoding and float64 in years with any GeoClient failures (2021, 2022, 2024).

**Key facts:**
- Year 2019 geocoded: 1,856/1,856 rows complete
- Year 2020 geocoded: 1,865/1,865 rows complete
- Year 2021 geocoded: 3,013/3,014 rows complete; `25H531` is a permanent GeoClient failure ("ADDRESS NUMBER OUT OF RANGE")
- Year 2022 geocoded: 1,960/1,968 rows complete; 8 permanent GeoClient failures (`05MAWW`, `17KBSP`, `24Z123`, `24Z124`, `24Z125`, `26QAJX`, `29QAXQ`, `31RAKL`)
- Year 2023 geocoded: 3,769/3,769 rows complete
- Year 2024 geocoded: 3,207/3,208 rows complete; `24Z124` is a permanent GeoClient failure
- Year 2025 geocoded: 3,630/3,630 rows complete
- The data is unique at the (`schooldbn`, `admission_process`) level
- Each `schooldbn` has exactly one address (verified)
- Column counts vary by year: 2019 (176), 2020 (183), 2021 (177), 2022 (129), 2023–2025 (167)
- Raw row counts: 2019 (3,057), 2020 (3,133), 2021 (4,799), 2022 (3,967), 2023 (5,911), 2024 (5,335), 2025 (5,781)
- `admission_process` values are always: 3K, PK, K

## Current state and remaining work

### 1. Geocode all years — COMPLETE

When adding corrections for a new year, the process requires the NYC GeoClient API key in `.env`. Ensure the format is:
```
    # url
    'SCHOOLDBN': {
        'INCORRECT ADDRESS':
        'ASSUMED CORRECT ADDRESS'
    },
```
This will allow me to manually test your results using google maps.

### 2. Transform steps — PARTIALLY COMPLETE

- **Merge geo** (`merge_geo.py`) — COMPLETE: joins geocoded CSVs onto raw site data on `schooldbn`
- **Reshape program codes** (`program_code_reshape.py`) — COMPLETE: reshapes wide `_progN` columns to long format; one row per `(schooldbn, admission_process, program_code)`
- **Coordinate transform** (`transform/main.py`) — COMPLETE: runs merge → reshape → saves to `data/transformed/`; called from `src/nycps_ece_sites/main.py`
- **Filter/select** — DEFERRED: reduce columns to only those needed for forecasting. Column list not yet specified.

### 3. Testing (`tests/`)

Use `pytest` (`uv run pytest`). Keep tests simple and focused. Test data should use small fixtures (hand-built DataFrames with a few rows), not the full dataset. Tests should not call the GeoClient API.

Fixtures live in `tests/conftest.py`: `raw_site_df` (mimics raw xlsx input) and `formatted_geo_df` (mimics output of `_00_set_up_geocode_df`, used as input for `_01`/`_02`). Note: `borough_list` is defined inside `_01_replace_borough`, not at module level — borough tests assert on known expected values rather than importing the list.

#### Remaining validation checks to migrate

**From `geocode.py` — geocode and merge:**
- `geocode_df`: output contains the expected response columns (`latitude`, `longitude`, `xCoordinate`, `yCoordinate`, `communityDistrict`)
- `merge_geocode`: merge is complete (no `left_only` or `right_only` rows); output row count matches input

**From `notebooks/explore.py` — data integrity (these apply to raw data per year):**
- Data is unique at (`schooldbn`, `admission_process`)
- Each `schooldbn` has exactly one `address`
- All `code_prog*` column values either start with the `schooldbn` value or are NA

#### Additional tests to write (not from existing code)

- **Extract**: `get_site_data` produces xlsx files in the expected location with expected naming
- **Schema stability**: Key columns (`schooldbn`, `admission_process`, `address`, `district`, `name`) are present in all years
- **Geocode output schema**: CSVs in `data/geocode/` have the expected 11 columns
- **Load interface** (once built): `load_sites(year)` returns the expected schema for each year; output is ready for joining on `schooldbn`

### 4. Load interface — COMPLETE

`load_sites(years)` in `pipeline/load.py` accepts a single year (int) or list of years and returns a concatenated DataFrame. Exported from `__init__.py` so the forecasting repo can call `from nycps_ece_sites import load_sites`. Reads from `src/nycps_ece_sites/data/transformed/` via a `__file__`-relative path, so it works both locally and when installed as a git dependency.

## Technical notes

- Package manager: `uv`
- Build backend: `uv_build`
- Python: 3.11+
- The geocode module uses `if __name__ == '__main__'` blocks extensively. These serve two purposes: (1) genuinely interactive debugging (inspecting individual API responses, experimenting with address corrections for a new year) and (2) validation logic that should be migrated into the test suite. Keep the interactive/exploratory blocks; migrate the validation checks into tests. See "Validation checks to migrate" below for the specific list.
- Address correction dicts in `geocode.py` are year-specific and maintained by hand — don't try to automate or restructure these unless asked
- `config_paths.py` finds the project root by walking up to `pyproject.toml` — all path references go through this module. Path constants: `RAW_DATA_DIR`, `GEOCODE_DIR`, `TRANSFORMED_DIR`

## Coding conventions

- Follow existing patterns in the codebase (function signatures, naming, docstring style)
- Use `pandas` for data manipulation
- Use `pathlib.Path` for file paths (via `config_paths`)
- Print progress with `print_output` flags, matching the existing style
- Keep `if __name__ == '__main__'` blocks for interactive use where they exist