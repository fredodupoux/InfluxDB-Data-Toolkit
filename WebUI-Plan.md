# Web UI Development Plan for InfluxDB Data Toolkit

This document outlines the steps to create a web-based user interface for the existing Python InfluxDB Data Toolkit.

## Phase 1: Basic Setup

1.  **Backend Framework**: Set up a basic Python Flask server (`server.py`).
    *   Add Flask to `requirements.txt`.
    *   Install dependencies.
2.  **Frontend Structure**: Create a basic HTML file (`templates/index.html`) to serve as the main page.
3.  **Serve Frontend**: Configure Flask to serve the `index.html` file.

## Phase 2: Expose Toolkit Functionality via API Endpoints

For each core feature of the toolkit, create corresponding API endpoints in `server.py`:

1.  **Export Data**:
    *   Endpoint (`/api/export`) to trigger the InfluxDB export process.
    *   Accept parameters like time range, bucket, measurement via POST request.
    *   Return status and potentially the path to the exported file or a preview.
2.  **List/Select CSV Files**:
    *   Endpoint (`/api/files`) to list available CSV files in the `_data` directory.
3.  **Clean Data**:
    *   Endpoint (`/api/clean`) to perform data cleaning operations.
    *   Accept CSV file path and cleaning parameters (columns to remove, filters, renames) via POST request.
    *   Return status and path to the cleaned file.
    *   Endpoint (`/api/preview`) to get a preview (e.g., first 5 rows, summary stats) of a CSV file.
4.  **Reformat Timestamps**:
    *   Endpoint (`/api/reformat_time`) to handle timestamp reformatting.
    *   Accept CSV file path and formatting options (timezone, keep time only) via POST request.
    *   Return status and path to the reformatted file.
5.  **Event Labeler**:
    *   Endpoint (`/api/launch_labeler`) - This is more complex. Initially, it might just trigger the existing `event_labeler_launcher.py` script.
    *   A full web-based labeler would require significant frontend development (Phase 4).

## Phase 3: Frontend Development (JavaScript)**

Develop the JavaScript frontend (`static/js/app.js`) to interact with the Flask API endpoints:

1.  **Export Form**: Create an HTML form to input export parameters. Use JavaScript to send a request to `/api/export`.
2.  **File Selection**: Display available CSV files fetched from `/api/files`. Allow users to select a file for cleaning/reformatting.
3.  **Data Preview**: Display data previews fetched from `/api/preview`.
4.  **Cleaning Interface**: Create UI elements (forms, buttons) to specify cleaning operations. Send requests to `/api/clean`.
5.  **Timestamp Reformatting Interface**: Create UI elements for timestamp options. Send requests to `/api/reformat_time`.
6.  **Status Updates**: Display feedback to the user (e.g., "Exporting...", "Cleaning complete", error messages).

## Phase 4: Advanced Features & Refinements

1.  **Web-Based Event Labeler**: Reimplement the event labeler's core logic and visualization using JavaScript libraries (e.g., Chart.js, D3.js) and interact with a dedicated backend API for data loading/saving.
2.  **Asynchronous Operations**: Handle long-running tasks (export, cleaning) asynchronously using techniques like WebSockets, server-sent events, or polling to avoid blocking the UI.
3.  **Configuration Management**: Allow editing `influxdb_config.json` and `water_event_rules.json` via the web UI.
4.  **Styling**: Apply CSS for a better user experience.
5.  **Error Handling**: Improve error reporting and handling on both frontend and backend.
6.  **Security**: Review security considerations, especially around file access and configuration.

## Technology Stack

*   **Backend**: Python, Flask
*   **Frontend**: HTML, CSS, JavaScript (potentially a framework like Vue.js or React later, but starting with vanilla JS)
*   **Libraries**: Pandas, InfluxDB Client (existing), potentially others for the web server.
