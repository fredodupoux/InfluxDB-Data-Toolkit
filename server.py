import os
from flask import Flask, render_template, jsonify, request
# Import necessary functions from your tools
# Removed unused import
from tools.exporter import export_data_from_influxdb
from tools.cleaner import apply_cleaning_operations # Import the new function
from tools.time_utils import reformat_timestamps_api # Import the timestamp reformatting function
import datetime # Needed for exporter timestamp
import pandas as pd # Needed for reading CSVs
import pytz # Needed for timezone validation

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure the _data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), '_data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

# --- API Endpoints ---

@app.route('/api/files', methods=['GET'])
def list_files():
    """Lists CSV files in the _data directory."""
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['POST'])
def handle_export():
    """Handles the data export request from the frontend."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body. Expected JSON."}), 400

        days = data.get('days', 3) # Default to 3 days if not provided
        device = data.get('device', 'WaterMeter') # Default device

        if not isinstance(days, int) or days <= 0:
             days_str = data.get('days', '3')
             try:
                 days = int(days_str)
                 if days <= 0:
                     raise ValueError("Days must be a positive integer.")
             except (ValueError, TypeError):
                 return jsonify({"error": "Invalid 'days' parameter. Must be a positive integer."}), 400


        if not device or not isinstance(device, str):
            return jsonify({"error": "Invalid 'device' parameter. Must be a non-empty string."}), 400

        # Load config and perform export using the refactored function
        # Config loading errors are handled within export_data_from_influxdb
        exported_filename = export_data_from_influxdb(days=days, device=device)

        # Return success response with the filename
        return jsonify({
            "message": "Export successful!",
            "filename": os.path.basename(exported_filename), # Return only the filename, not the full path
            "fullPath": exported_filename # Keep full path for server-side use if needed later
        }), 200

    except FileNotFoundError as e:
         print(f"Export Error: Config file not found - {e}")
         return jsonify({"error": f"Configuration file missing: {e}. Please ensure 'config/influxdb_config.json' exists and is correctly formatted."}), 500
    except ValueError as e:
         print(f"Export Error: Invalid input - {e}")
         return jsonify({"error": f"Invalid input: {e}"}), 400
    except Exception as e:
        # Catch other potential errors from export_data_from_influxdb
        print(f"Export Error: {e}") # Log the full error server-side
        # Return a generic error message to the client
        return jsonify({"error": f"An unexpected error occurred during export: {e}"}), 500

@app.route('/api/preview', methods=['POST'])
def handle_preview():
    """Provides a preview of a selected CSV file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({"error": "Missing 'filename' in request body."}), 400

        # Construct the full path safely
        file_path = os.path.join(DATA_DIR, os.path.basename(filename)) # Use basename to prevent path traversal

        if not os.path.exists(file_path) or not file_path.startswith(DATA_DIR):
             return jsonify({"error": f"File not found or invalid path: {filename}"}), 404

        df = pd.read_csv(file_path)

        # Generate preview data
        preview = {
            "filename": os.path.basename(filename),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "head": df.head().to_dict(orient='records'), # First 5 rows as list of dicts
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        return jsonify(preview), 200

    except pd.errors.EmptyDataError:
        return jsonify({"error": f"File is empty: {filename}"}), 400
    except Exception as e:
        print(f"Preview Error: {e}")
        return jsonify({"error": f"An error occurred while generating preview: {e}"}), 500

@app.route('/api/clean', methods=['POST'])
def handle_clean():
    """Applies cleaning operations to a specified CSV file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        operations = data.get('operations')

        if not filename or not isinstance(operations, list):
            return jsonify({"error": "Missing 'filename' or invalid 'operations' list in request body."}), 400

        # Construct the full path safely
        file_path = os.path.join(DATA_DIR, os.path.basename(filename))

        if not os.path.exists(file_path) or not file_path.startswith(DATA_DIR):
             return jsonify({"error": f"File not found or invalid path: {filename}"}), 404

        # Load the dataframe
        df = pd.read_csv(file_path)

        # Apply cleaning operations using the refactored function
        df_cleaned = apply_cleaning_operations(df, operations)

        # Save the cleaned dataframe
        base_name = os.path.splitext(os.path.basename(filename))[0]
        # Append _clean suffix, potentially multiple times
        new_filename_base = f"{base_name}_clean"
        # To avoid excessively long names, maybe limit the number of _clean suffixes or use timestamp
        # Example: Use timestamp to ensure uniqueness if name gets too long or complex
        # new_filename_base = f"{base_name}_clean_{timestamp}"
        new_filename = f"{new_filename_base}.csv"
        new_file_path = os.path.join(DATA_DIR, new_filename)

        df_cleaned.to_csv(new_file_path, index=False)
        print(f"Cleaned data saved to {new_file_path}") # Server log

        return jsonify({
            "message": "Cleaning successful!",
            "originalFilename": os.path.basename(filename),
            "cleanedFilename": new_filename,
            "fullPath": new_file_path
        }), 200

    except (FileNotFoundError, KeyError, ValueError) as e:
         # Specific errors from apply_cleaning_operations or file loading
         print(f"Cleaning Error: {e}")
         return jsonify({"error": f"Cleaning failed: {e}"}), 400
    except pd.errors.EmptyDataError:
        return jsonify({"error": f"Cannot clean an empty file: {filename}"}), 400
    except Exception as e:
        print(f"Cleaning Error: {e}")
        return jsonify({"error": f"An unexpected error occurred during cleaning: {e}"}), 500

# --- New Endpoint for Timestamp Reformatting ---
@app.route('/api/reformat_time', methods=['POST'])
def handle_reformat_time():
    """Handles timestamp reformatting requests."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        target_timezone = data.get('targetTimezone', 'America/New_York') # Default timezone
        convert_timezone = data.get('convertTimezone', False)
        keep_time_only = data.get('keepTimeOnly', False)

        if not filename:
            return jsonify({"error": "Missing 'filename' in request body."}), 400
        if not isinstance(convert_timezone, bool):
             return jsonify({"error": "'convertTimezone' must be a boolean."}), 400
        if not isinstance(keep_time_only, bool):
             return jsonify({"error": "'keepTimeOnly' must be a boolean."}), 400
        if convert_timezone and target_timezone:
             try:
                 pytz.timezone(target_timezone) # Validate timezone early
             except pytz.exceptions.UnknownTimeZoneError:
                 return jsonify({"error": f"Invalid target timezone specified: {target_timezone}"}), 400

        # Construct the full path safely
        file_path = os.path.join(DATA_DIR, os.path.basename(filename)) # Use basename to prevent path traversal

        if not os.path.exists(file_path) or not file_path.startswith(DATA_DIR):
             return jsonify({"error": f"File not found or invalid path: {filename}"}), 404

        # Call the refactored API function
        reformatted_file_path = reformat_timestamps_api(
            csv_file_path=file_path,
            target_timezone=target_timezone,
            convert_timezone=convert_timezone,
            keep_time_only=keep_time_only
        )

        return jsonify({
            "message": "Timestamp reformatting successful!",
            "originalFilename": os.path.basename(filename),
            "reformattedFilename": os.path.basename(reformatted_file_path),
            "fullPath": reformatted_file_path
        }), 200

    except FileNotFoundError as e:
        print(f"Reformat Error: {e}")
        return jsonify({"error": str(e)}), 404
    except (KeyError, ValueError) as e: # Catch errors like missing '_time' or bad timezone from API
        print(f"Reformat Error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Reformat Error: An unexpected error occurred - {e}")
        return jsonify({"error": f"An unexpected error occurred during timestamp reformatting: {e}"}), 500


# Add more endpoints here later for clean, reformat, etc.

if __name__ == '__main__':
    # Ensure static files are served correctly in debug mode
    app.run(debug=True, port=5001)
