#!/usr/bin/env python
"""
Event Labeler - Command Line Script

This script launches the water event labeling tool.
"""

# Updated import path to correctly reference the event_labeler module from the tools directory
import sys
import os

# Add the parent directory to the path so we can import event_labeler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from event_labeler import main

if __name__ == "__main__":
    main()