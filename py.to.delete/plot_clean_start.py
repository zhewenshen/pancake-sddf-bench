#!/usr/bin/env python3
"""
Detailed comparison plots with raw values (top) and relative differences (bottom) for each metric.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import sys
from pathlib import Path
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')

def load_data(csv_file):
    """Load CSV data into a pandas DataFrame and filter out incomplete records."""
    df = pd.read_csv(csv_file)
    
    # Filter out rows where critical metrics are NaN (incomplete records)
    # Use 'Kernel Cycles' as indicator since it should always be present for complete records
    df = df[df['Kernel Cycles'].notna()]
    
    # Reset index after filtering
    df = df.reset_index(drop=True)
    
    print(f"Loaded {len(df)} complete records (filtered out incomplete ones)")
    return df

def calculate_relative_diff(baseline, comparison):
    """Calculate relative difference as percentage: (comparison - baseline) / baseline * 100"""
    return ((comparison - baseline) / baseline) * 100

def create_comparison_plot(ax1, ax2, x_positions, x_labels, y1, y2, ylabel, title, label1, label2, use_bars=True):
    """Create a standard comparison plot with raw values (top) and relative diff (bottom)."""
    
    # Top plot: Raw comparison
    if use_bars:
        width = 0.35
        x1 = np.array(x_positions) - width/2
        x2 = np.array(x_positions) + width/2
        
        bars1 = ax1.bar(x1, y1, width, label=label1, color='#5D6D7E', alpha=0.9)  # Soft gray
        bars2 = ax1.bar(x2, y2, width, label=label2, color='#85C1E9', alpha=0.9)  # Soft light blue
        
        # Add data labels on bars
        for bar, val in zip(bars1, y1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
