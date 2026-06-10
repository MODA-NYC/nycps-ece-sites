# nycps-ece-sites
Generate data on NYCPS ECE sites

## Using this package

Install as a git dependency:

```sh
uv add git+https://github.com/MODA-NYC/nycps-ece-sites.git
```

Then load site data for one or more years:

```python
from nycps_ece_sites import load_sites

# Single year
df = load_sites(2025)

# Multiple years — returns a concatenated DataFrame
df = load_sites([2023, 2024, 2025])
```

The returned DataFrame is at `(schooldbn, admission_process, program_code)` grain and includes geocoded coordinates, community district, and program-level admissions data.

## Geo-coding

1. Sign into [NYC API Developer's Portal](https://api-portal.nyc.gov/)
2. Request API key by subscribing to the [GeoClient V2 API](https://api-portal.nyc.gov/api-details#api=geoclient-current-v2&operation=get-address-housenumber-housenumber-street-street)
3. Save in `.env` folder as `NYC_API = ''`

### Miscellaneous notes

The data on sites has columns that are extraneous for current purposes, but may be of interest for future research. For example the 2025 directory data contains:
* Data on 14 admissions priorities for all programs (currently in a wide format; see `[priority1_prog1, ..., priority14_prog1, ... priority14_prog7]` ). If doing research on admissions priorities, it would be valuable to reshape data to the program level
