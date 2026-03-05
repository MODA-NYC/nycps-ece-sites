# nycps-ece-sites
Generate data on NYCPS ECE sites

## Geo-coding

1. Sign into [NYC API Developer's Portal](https://api-portal.nyc.gov/)
2. Request API key by subscribing to the [GeoClient V2 API](https://api-portal.nyc.gov/api-details#api=geoclient-current-v2&operation=get-address-housenumber-housenumber-street-street)
3. Save in `.env` folder as `NYC_API = ''`

### Miscellaneous notes

The data on sites has columns that are extraneous for current purposes, but may be of interest for future research. For example the 2025 directory data contains:
* Data on 14 admissions priorities for all programs (currently in a wide format; see `[priority1_prog1, ..., priority14_prog1, ... priority14_prog7]` ). If doing research on admissions priorities, it would be valuable to reshape data to the program level
