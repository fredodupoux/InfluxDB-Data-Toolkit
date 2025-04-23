"""
Machine Learning Preparation Notice

The ML preparation functionality has been removed from this project as it is now
being handled in Google Colab instead.

Please use the following workflow:
1. Use the event_labeler module to label your water consumption events
2. Export the labeled data as CSV
3. Upload the CSV to Google Colab for machine learning tasks

For any ML-specific functionality, please refer to the Google Colab notebooks.
"""

def prepare_data_for_ml(csv_file=None):
    """
    This function previously contained ML preparation functionality, which has now been moved to Google Colab.
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to the CSV file to process (no longer used)
        
    Returns:
    --------
    None
    """
    print("\n" + "="*60)
    print("⚠️ ML Preparation Notice ⚠️".center(60))
    print("="*60)
    print("The ML preparation toolkit has been removed from this project.")
    print("ML tasks are now handled in Google Colab for improved performance and flexibility.")
    print("\nRecommended workflow:")
    print("1. Use the event_labeler module to label your water consumption events")
    print("2. Export the labeled data as CSV")
    print("3. Upload the CSV to Google Colab for machine learning analysis")
    print("\nTo launch the event labeler, run: python -m tools.run_event_labeler")
    
    return None