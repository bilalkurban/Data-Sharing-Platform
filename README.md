DATA DISSEMINATION PLATFORM
===========================

This repository contains a Streamlit application designed to support interactive data exploration, visualization, download, and API access for reserve assets or similar financial datasets. Developed for the Central Bank of Malta, the tool simplifies access to structured and clean data for both internal and external users.

KEY FEATURES
------------
- Filterable interface by observation date, currency, item, and maturity
- Time-series mode and multiple chart options (Bar, Column, Line, Pie)
- Download filtered results as CSV or Excel
- Built-in, example-ready API URL generator for programmatic access
- Simulated API server documentation and integration examples
- API key generation and basic API usage tracking (session-based)

REQUIREMENTS
------------
Python 3.9 or above

Install dependencies:
```
pip install -r requirements.txt
```

**requirements.txt**
```
streamlit
pandas
plotly
openpyxl
```

USAGE
-----
To run locally:

```
streamlit run app.py
```

To deploy on Streamlit Cloud:
1. Push this repository to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your GitHub and deploy this repo
4. Upload or link to your Excel data file (replace 'your_data_file.xlsx')

EXPECTED FILES
--------------
- `app.py`               : Main Streamlit application
- `your_data_file.xlsx`  : Data file (expected on Sheet 3, index 2)
- `requirements.txt`     : Python dependencies

DATA FILE FORMAT
----------------
Your Excel file should contain a sheet with the following columns:

- `OBS_DATE`             : Observation date (datetime)
- `ITEM`                 : Financial instrument/item name
- `CURRENCY`             : Currency code (e.g., USD, EUR)
- `RESIDUAL_MATURITY`    : Maturity category (e.g., 1Y, 3M)
- `AMOUNT`               : Numeric value

CREDITS
-------
Developed by Bilal Kurban  
For: Central Bank of Malta Statistics Department  
Streamlit-powered open data prototype (May 2025)

LICENSE
-------
Internal use. Please consult with the Central Bank of Malta for reuse permissions.
