"""
Visualization Module for Water Event Labeler

This module provides specialized visualization functions for analyzing water consumption events.
It includes:

- Individual event visualization with detailed metrics (volume, flow rate, duration)
- Cluster visualization to identify patterns in water usage via K-means clustering
- Time pattern analysis to detect usage patterns throughout the day
- Interactive plotting for manual labeling assistance

The visualizations help users identify different types of water fixtures (showers, toilets, 
faucets, etc.) based on their characteristic patterns of water consumption.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# Set plot style
sns.set_style("whitegrid")

def visualize_event(df, event_idx):
    """
    Visualize a single water consumption event for manual labeling.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events
    event_idx : int
        Index of the event to visualize
    
    Returns:
    --------
    None
    """
    event = df.iloc[event_idx]
    
    # Create a figure with subplots
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Bar chart for key metrics
    metrics = ['avgFlowRate', 'eventLength', 'eventVolume', 'maxFlowRate']
    values = [event[metric] for metric in metrics]
    
    # Normalize eventLength for better visualization if it's much larger than other values
    if event['eventLength'] > 100:
        normalized_length = event['eventLength'] / 60  # Convert to minutes
        values[1] = normalized_length
        metrics[1] = 'eventLength (min)'
    
    ax.bar(metrics, values, color=['royalblue', 'lightgreen', 'coral', 'purple'])
    ax.set_title(f"Water Event at {event['time']}")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of each bar
    for i, v in enumerate(values):
        ax.text(i, v + 0.1, f"{v:.2f}", ha='center')
    
    # Add event information as text
    info_text = (f"Time: {event['time']}\n"
                 f"Event Length: {event['eventLength']} sec\n"
                 f"Event Volume: {event['eventVolume']} gallons\n"
                 f"Avg Flow Rate: {event['avgFlowRate']} GPM\n"
                 f"Max Flow Rate: {event['maxFlowRate']} GPM")
    
    if 'label' in df.columns and pd.notna(event['label']) and event['label'] != '':
        info_text += f"\nCurrent Label: {event['label']}"
    
    plt.figtext(0.02, 0.02, info_text, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)  # Small pause to ensure the plot appears


def visualize_clusters(df, feature_cols=['eventLength', 'eventVolume', 'avgFlowRate', 'maxFlowRate'], n_clusters=6):
    """
    Visualize clusters of water events to help with labeling.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events
    feature_cols : list
        List of columns to use for clustering
    n_clusters : int
        Number of clusters to create
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with cluster assignments
    """
    # Prepare data for clustering
    X = df[feature_cols].copy()
    
    # Handle any missing values
    X = X.fillna(X.mean())
    
    # Normalize data for clustering
    X_scaled = (X - X.mean()) / X.std()
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add cluster assignments to dataframe
    df_with_clusters = df.copy()
    df_with_clusters['cluster'] = clusters
    
    # Create scatter plot matrix
    plt.figure(figsize=(12, 10))
    sns.pairplot(df_with_clusters, vars=feature_cols, hue='cluster', palette='tab10', corner=True)
    plt.suptitle('Water Event Clusters', y=1.02, fontsize=16)
    
    # Create a more detailed plot of the most important features
    plt.figure(figsize=(10, 6))
    plt.scatter(df['eventLength'], df['eventVolume'], 
                c=clusters, cmap='tab10', alpha=0.7, s=df['maxFlowRate']*30)
    plt.xlabel('Event Length (seconds)')
    plt.ylabel('Event Volume (gallons)')
    plt.title('Water Events by Length and Volume')
    plt.colorbar(label='Cluster')
    
    # Add annotations for cluster centers
    centers = kmeans.cluster_centers_
    for i, center in enumerate(centers):
        center_actual = center * X.std().values + X.mean().values
        plt.annotate(f'Cluster {i}', 
                    (center_actual[0], center_actual[1]),
                    fontsize=10,
                    color='black',
                    backgroundcolor='white',
                    ha='center')
    
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)  # Small pause to ensure the plot appears
    
    return df_with_clusters


def visualize_time_patterns(df):
    """
    Visualize events by time of day to identify patterns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events with a time column
    
    Returns:
    --------
    None
    """
    # Convert time to hour of day
    df = df.copy()
    
    if pd.api.types.is_datetime64_any_dtype(df['time']):
        df['hour'] = df['time'].dt.hour + df['time'].dt.minute / 60
    else:
        # Try to extract hour from time string
        try:
            time_strings = df['time'].astype(str)
            hours = [int(t.split(':')[0]) for t in time_strings]
            minutes = [int(t.split(':')[1]) for t in time_strings]
            df['hour'] = [h + m/60 for h, m in zip(hours, minutes)]
        except Exception as e:
            print(f"⚠️ Warning: Could not extract hour from time column: {str(e)}")
            return
    
    # Create figure with multiple subplots
    fig, axs = plt.subplots(2, 1, figsize=(12, 12), gridspec_kw={'height_ratios': [1, 2]})
    
    # Plot 1: Histogram of events by hour
    axs[0].hist(df['hour'], bins=24, color='skyblue', edgecolor='black')
    axs[0].set_title('Distribution of Water Events by Hour of Day')
    axs[0].set_xlabel('Hour of Day')
    axs[0].set_ylabel('Number of Events')
    axs[0].set_xticks(range(0, 24, 2))
    axs[0].grid(True, alpha=0.3)
    
    # Plot 2: Scatter plot of event characteristics by hour
    scatter = axs[1].scatter(df['hour'], df['eventLength'], 
                            s=df['eventVolume']*50, 
                            c=df['maxFlowRate'], 
                            cmap='viridis', 
                            alpha=0.6)
    
    axs[1].set_title('Water Event Characteristics by Hour of Day')
    axs[1].set_xlabel('Hour of Day')
    axs[1].set_ylabel('Event Length (seconds)')
    axs[1].set_xticks(range(0, 24, 2))
    axs[1].grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=axs[1])
    cbar.set_label('Max Flow Rate (GPM)')
    
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)  # Small pause to ensure the plot appears