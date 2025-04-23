#!/usr/bin/env python
"""
Event Labeler Launcher Script

This script serves as the entry point for launching the Water Event Labeler application
from the tools directory. It handles:

- Proper path setup to ensure the event_labeler module can be imported 
  regardless of the current working directory
- Streamlined launching of the event labeler's main function
- Integration with the main InfluxDB Data Toolkit application

The script is designed to be called either directly or from the parent 
influx_data_toolkit.py application.
"""

# Updated import path to correctly reference the event_labeler module from the tools directory
import sys
import os

# Add the parent directory to the path so we can import event_labeler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from event_labeler import main

if __name__ == "__main__":
    main()