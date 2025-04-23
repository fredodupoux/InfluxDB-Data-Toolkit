# InfluxDB Data Toolkit

A comprehensive Python toolkit for exporting, cleaning, processing, and preparing time series data from InfluxDB for machine learning, primarily designed for working with water meter data.

## Features

- 🔄 **Export Data**: Query and export data from InfluxDB with customizable parameters
- 🧹 **Clean Data**: Interactive data cleaning tool with options to remove columns, filter values, and rename columns
- 🕒 **Reformat Timestamps**: Convert timestamps to different timezones and formats, with options to keep only time components
- 📊 **Data Visualization**: Preview data and statistics directly in the console
- 🔒 **Secure Credentials**: Store InfluxDB credentials securely, protected from Git
- 🧠 **ML Preparation**: Advanced machine learning data preparation tools including:
  - Feature engineering and extraction
  - Anomaly detection
  - Data visualization for ML features
  - Feature distribution analysis
  - Data normalization and scaling

## Requirements

- Python 3.6+
- pandas
- influxdb-client
- pytz
- matplotlib
- scikit-learn
- numpy

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
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
4. Launch ML preparation tool
5. Exit program

## Data Cleaning Features

The toolkit provides powerful data cleaning capabilities:
- Remove columns from datasets
- Filter data based on column values (equals, less than, greater than)
- Rename individual columns or multiple columns at once
- View summary statistics of your data
- Preview data before and after operations

## Timestamp Formatting Options

The timestamp formatter now supports multiple operations:
- Convert timestamps between different timezones
- Remove date components (keep only time values)
- Combine both operations at once
- Clear naming convention for processed files (_time_only, _tz_converted, etc.)

## ML Preparation Tool

The ML preparation tool provides specialized functionality for preparing time series data for machine learning:

```bash
python ml_toolkit.py [optional_csv_file]
```

Features include:
- Feature extraction from time series data
- Statistical analysis and visualization of features
- Anomaly detection using various algorithms
- Data normalization and scaling options
- Export of ML-ready datasets

## Example Workflow

1. Export data from InfluxDB (providing credentials if needed)
2. Preview the exported data
3. Reformat timestamps to your local timezone
4. Clean the data by removing unnecessary columns or filtering values
5. Use the ML preparation tool to engineer features and analyze the data
6. Export prepared data for use with machine learning models

## License

This project is licensed under the MIT License - see the LICENSE file for details.