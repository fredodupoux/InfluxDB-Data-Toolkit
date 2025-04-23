"""
Event Labeler - Water Consumption Event Classification Tool

This package helps label water consumption events from time series data for machine learning.
It allows both rule-based auto-labeling and manual labeling of water usage events
(e.g., shower, dishwasher, washing machine, faucet, etc.).
"""

from .core import load_data, manually_label_events, train_test_split_by_time
from .visualization import visualize_event, visualize_clusters, visualize_time_patterns
from .rules import define_labeling_rules, apply_rules, save_rules, load_rules
from .main import main

__version__ = '1.0.0'