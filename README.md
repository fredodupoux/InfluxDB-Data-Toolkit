# InfluxDB Data Toolkit

A comprehensive Python toolkit for exporting, cleaning, and processing time series data from InfluxDB, primarily designed for working with water meter data.

## Features

- 🔄 **Export Data**: Query and export data from InfluxDB with customizable parameters
- 🧹 **Clean Data**: Interactive data cleaning tool with options to remove columns and filter values
- 🕒 **Reformat Timestamps**: Convert timestamps to different timezones and formats
- 📊 **Data Visualization**: Preview data and statistics directly in the console
- 🔒 **Secure Credentials**: Store InfluxDB credentials securely, protected from Git

## Requirements

- Python 3.6+
- pandas
- influxdb-client
- pytz

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install pandas influxdb-client pytz
   ```

## Usage

Run the script with:

```bash
python influx_data_toolkit.py
```

The interactive menu will guide you through the available options:

1. Export data from InfluxDB
2. Clean existing CSV data for machine learning
3. Reformat timestamps and adjust timezone
4. Exit program

## Security Notes

- InfluxDB credentials are stored in a `influxdb_config.json` file
- This file is included in `.gitignore` to prevent accidental exposure
- The script will prompt for credentials on first run

## Example Workflow

1. Export data from InfluxDB (providing credentials if needed)
2. Preview the exported data
3. Reformat timestamps to your local timezone
4. Clean the data by removing unnecessary columns or filtering values
5. Use the cleaned data for analysis or machine learning

## License

This project is licensed under the MIT License - see the LICENSE file for details.