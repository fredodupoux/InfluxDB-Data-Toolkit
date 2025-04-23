#!/usr/bin/env python
"""
Event Labeler Launcher - InfluxDB Data Toolkit extension

This script provides an entry point to the water event labeling system,
which helps prepare data for later analysis in Google Colab.
"""

import os
import sys

print("\n🔄 Loading event labeler module...")

# Import the event labeler functionality
try:
    from event_labeler import main as event_labeler_main
    HAS_EVENT_LABELER = True
except ImportError:
    print("⚠️ Event labeler module not found. Please ensure the event_labeler directory is in your project.")
    HAS_EVENT_LABELER = False

def main():
    """Main entry point for the event labeler launcher"""
    # Show welcome message
    print("\n" + "="*60)
    print("🌟 Water Event Labeler 🌟".center(60))
    print("="*60)
    print("This tool helps label water consumption events in your time series data.")
    print("The labeled data can then be used for machine learning in Google Colab.")
    
    # Check for any command line arguments for CSV file
    initial_file = None
    if len(sys.argv) > 1:
        potential_file = sys.argv[1]
        if os.path.exists(potential_file) and potential_file.endswith('.csv'):
            initial_file = potential_file
            print(f"\n📄 Found CSV file from command line: {initial_file}")
    
    # Launch the event labeler
    if HAS_EVENT_LABELER:
        print("\n📊 Launching Water Event Labeler...")
        event_labeler_main(initial_file)
    else:
        print("❌ Event labeler module is not available.")
        print("Please make sure the event_labeler directory is in your project.")
        input("\n⏸️ Press Enter to exit...")

if __name__ == "__main__":
    main()