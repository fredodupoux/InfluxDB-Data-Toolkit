# InfluxDB Data Toolkit

A comprehensive Python toolkit for exporting, cleaning, processing, and preparing time series data from InfluxDB for machine learning, primarily designed for working with water meter data.

## Features

- 🔄 **Export Data**: Query and export data from InfluxDB with customizable parameters
- 🧹 **Clean Data**: Interactive data cleaning tool with options to remove columns, filter values, and rename columns
- 🕒 **Reformat Timestamps**: Convert timestamps to different timezones and formats, with options to keep only time components
- 📊 **Data Visualization**: Preview data and statistics directly in the console
- 🔒 **Secure Credentials**: Store InfluxDB credentials securely, protected from Git
- 🏷️ **Event Labeling**: Interactive event labeling system for past water consumption data

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
4. Launch event labeler tool
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

## Event Labeler Tool

The event labeler tool provides an interactive interface for labeling water consumption events in your time series data:

```bash
python event_labeler_launcher.py [optional_csv_file]
```

Features include:
- Interactive visualization of water consumption data
- Configurable rules for event detection
- Manual labeling of water consumption events
- Export of labeled datasets for further analysis in Google Colab

## Example Workflow

1. Export data from InfluxDB (providing credentials if needed)
2. Preview the exported data
3. Reformat timestamps to your local timezone
4. Clean the data by removing unnecessary columns or filtering values
5. Use the event labeler to identify and label water consumption events
6. Export labeled data for use with machine learning models in Google Colab

## License

This project is licensed under the MIT License - see the LICENSE file for details.