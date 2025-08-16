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
    
    # Round values to match what will be displayed
    y1_displayed = np.array([float(f'{val:.1f}') if val >= 10 else float(f'{val:.2f}') for val in y1])
    y2_displayed = np.array([float(f'{val:.1f}') if val >= 10 else float(f'{val:.2f}') for val in y2])
    
    # Top plot: Raw comparison
    if use_bars:
        width = 0.35
        x1 = np.array(x_positions) - width/2
        x2 = np.array(x_positions) + width/2
        
        bars1 = ax1.bar(x1, y1, width, label=label1, color='#5D6D7E', alpha=0.9)  # Soft gray
        bars2 = ax1.bar(x2, y2, width, label=label2, color='#85C1E9', alpha=0.9)  # Soft light blue
        
        # Add data labels on bars
        for bar, val, disp_val in zip(bars1, y1, y1_displayed):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                    ha='center', va='bottom', fontsize=8, color='#5D6D7E')
        
        for bar, val, disp_val in zip(bars2, y2, y2_displayed):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                    ha='center', va='bottom', fontsize=8, color='#85C1E9')
    else:
        ax1.plot(x_positions, y1, 'o-', label=label1, linewidth=2, markersize=8, color='#5D6D7E')  # Soft gray
        ax1.plot(x_positions, y2, 's-', label=label2, linewidth=2, markersize=8, color='#85C1E9')  # Soft light blue
        
        # Add data labels on line points
        for x, val, disp_val in zip(x_positions, y1, y1_displayed):
            ax1.text(x, val + max(y1)*0.02, f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                    ha='center', va='bottom', fontsize=8, color='#5D6D7E')
        
        for x, val, disp_val in zip(x_positions, y2, y2_displayed):
            ax1.text(x, val + max(y2)*0.02, f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                    ha='center', va='bottom', fontsize=8, color='#85C1E9')
    
    ax1.set_ylabel(ylabel, fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(x_labels, rotation=45)
    
    # Bottom plot: Relative difference - use displayed values for consistency
    rel_diff = calculate_relative_diff(y1_displayed, y2_displayed)
    colors = ['#27AE60' if x >= 0 else '#E67E22' for x in rel_diff]  # Simple green for positive, simple orange for negative
    bars = ax2.bar(x_positions, rel_diff, color=colors, alpha=0.8)
    
    ax2.set_xlabel('Requested Throughput (Mb/s)', fontsize=12)
    ax2.set_ylabel('Relative Difference (%)', fontsize=12)
    ax2.set_title(f'Relative Difference ({label2} vs {label1})', fontsize=12)
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(x_labels, rotation=45)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars, rel_diff):
        height = bar.get_height()
        if abs(height) > 0.1:  # Only show labels for non-zero differences
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', fontsize=8)

def save_plot(fig, pdf, svg_dir, filename):
    """Save plot to both PDF and SVG (if svg_dir provided)."""
    plt.tight_layout()
    pdf.savefig(fig)
    if svg_dir:
        plt.savefig(svg_dir / f'{filename}.svg', format='svg', bbox_inches='tight')
    plt.close()

def plot_instructions_per_second(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot instructions per second comparison."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    inst_per_sec1 = df1['Instructions per Second'] / 1e9  # Convert to billions
    inst_per_sec2 = df2['Instructions per Second'] / 1e9
    
    create_comparison_plot(ax1, ax2, x_positions, x_labels, inst_per_sec1, inst_per_sec2,
                          'Instructions per Second (Billions)', 'Instructions per Second vs Throughput',
                          label1, label2)
    
    save_plot(fig, pdf, svg_dir, '01_instructions_per_second')

def plot_throughput_vs_cpu(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot requested vs received throughput with CPU utilization overlay."""
    
    fig, ax1 = plt.subplots(1, 1, figsize=(12, 8))
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    # Throughput bars with CPU utilization line
    width = 0.35
    x1 = np.array(x_positions) - width/2
    x2 = np.array(x_positions) + width/2
    
    # Throughput bars
    bars1 = ax1.bar(x1, df1['Recv Thrput (Mb/s)'], width, label=f'{label1} Recv Throughput', 
                    color='#5D6D7E', alpha=0.9)  # Soft gray
    bars2 = ax1.bar(x2, df2['Recv Thrput (Mb/s)'], width, label=f'{label2} Recv Throughput', 
                    color='#85C1E9', alpha=0.9)  # Soft light blue
    
    # Add data labels on throughput bars
    for bar, val in zip(bars1, df1['Recv Thrput (Mb/s)']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{val:.1f}',
                ha='center', va='bottom', fontsize=8, color='#5D6D7E')
    
    for bar, val in zip(bars2, df2['Recv Thrput (Mb/s)']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{val:.1f}',
                ha='center', va='bottom', fontsize=8, color='#85C1E9')
    
    ax1.set_xlabel('Requested Throughput (Mb/s)', fontsize=12)
    ax1.set_ylabel('Received Throughput (Mb/s)', fontsize=12)
    ax1.set_title('Received Throughput vs Requested with CPU Utilization Overlay', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(x_labels, rotation=45)
    
    # CPU utilization on secondary y-axis
    ax2 = ax1.twinx()
    cpu_util1 = df1['CPU Util (Fraction)'] * 100
    cpu_util2 = df2['CPU Util (Fraction)'] * 100
    
    line1 = ax2.plot(x_positions, cpu_util1, 'o-', label=f'{label1} CPU Util', 
                     linewidth=3, markersize=8, color='#2C3E50')  # Dark blue-gray
    line2 = ax2.plot(x_positions, cpu_util2, 's-', label=f'{label2} CPU Util', 
                     linewidth=3, markersize=8, color='#000000')  # Black
    
    # Add data labels on CPU utilization line points
    for x, val in zip(x_positions, cpu_util1):
        ax2.text(x, val + 2, f'{val:.1f}%',
                ha='center', va='bottom', fontsize=8, color='#2C3E50')
    
    for x, val in zip(x_positions, cpu_util2):
        ax2.text(x, val + 2, f'{val:.1f}%',
                ha='center', va='bottom', fontsize=8, color='#000000')
    
    ax2.set_ylabel('CPU Utilization (%)', fontsize=12)
    ax2.set_ylim(0, 105)  # Set scale from 0 to 105%
    ax2.grid(True, alpha=0.2, linestyle='--')
    
    # Combined legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', fontsize=10)
    
    save_plot(fig, pdf, svg_dir, '02_throughput_vs_cpu')

def plot_comprehensive_cpu_utilization(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot comprehensive CPU utilization using standard format with Total System + components."""
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    # Get system total CPU utilization
    total_util1 = df1['CPU Util (Fraction)'] * 100
    total_util2 = df2['CPU Util (Fraction)'] * 100
    
    # System total plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    create_comparison_plot(ax1, ax2, x_positions, x_labels, total_util1, total_util2,
                          'CPU Utilization (%)', 'Total System CPU Utilization vs Throughput',
                          label1, label2, use_bars=True)
    save_plot(fig, pdf, svg_dir, '03_total_cpu_utilization')
    
    # Plot each component separately using standard format
    components = ['ethernet_driver', 'net_virt_tx', 'net_virt_rx', 'client0', 'client0_net_copier']
    component_names = ['Ethernet Driver CPU Utilization', 'Net Virt TX CPU Utilization', 
                       'Net Virt RX CPU Utilization', 'Client0 CPU Utilization', 'Client0 Net Copier CPU Utilization']
    
    for i, (component, name) in enumerate(zip(components, component_names)):
        cpu_col = f'{component}_CPU_Util'
        if cpu_col in df1.columns and cpu_col in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            util1 = df1[cpu_col]
            util2 = df2[cpu_col]
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, util1, util2,
                                  'CPU Utilization (%)', f'{name} vs Throughput',
                                  label1, label2, use_bars=True)
            
            save_plot(fig, pdf, svg_dir, f'04_{component}_utilization')

def plot_cpu_utilization(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot CPU utilization comparison."""
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    # CPU Utilization percentage
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    cpu_util1 = df1['CPU Util (Fraction)'] * 100
    cpu_util2 = df2['CPU Util (Fraction)'] * 100
    
    create_comparison_plot(ax1, ax2, x_positions, x_labels, cpu_util1, cpu_util2,
                          'CPU Utilization (%)', 'System CPU Utilization vs Throughput',
                          label1, label2)
    
    save_plot(fig, pdf, svg_dir, '05_system_cpu_utilization')
    
    # Raw CPU cycle metrics
    raw_cpu_metrics = [
        ('Total Cycles', 'Total CPU Cycles'),
        ('Kernel Cycles', 'Kernel CPU Cycles'),
        ('User Cycles', 'User CPU Cycles'),
        ('Idle Cycles', 'Idle CPU Cycles')
    ]
    
    for i, (metric, title) in enumerate(raw_cpu_metrics):
        if metric in df1.columns and metric in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            values1 = df1[metric] / 1e9  # Convert to billions for readability
            values2 = df2[metric] / 1e9
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  f'{metric} (Billions)', f'{title} vs Throughput',
                                  label1, label2)
            
            save_plot(fig, pdf, svg_dir, f'06_{metric.lower().replace(" ", "_")}_cycles')

def plot_cache_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot cache metrics comparisons."""
    
    # Raw cache metrics (total counts)
    raw_cache_metrics = [
        ('L1 I-cache misses', 'L1 I-cache Misses (Total)'),
        ('L1 D-cache misses', 'L1 D-cache Misses (Total)'),
        ('L1 I-TLB misses', 'L1 I-TLB Misses (Total)'),
        ('L1 D-TLB misses', 'L1 D-TLB Misses (Total)'),
        ('Instructions', 'Instructions (Total)'),
        ('Branch mispredictions', 'Branch Mispredictions (Total)')
    ]
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    # Plot raw cache metrics
    for i, (metric, title) in enumerate(raw_cache_metrics):
        if metric in df1.columns and metric in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            values1 = df1[metric] / 1e6  # Convert to millions for readability
            values2 = df2[metric] / 1e6
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  f'{title.replace("(Total)", "(Millions)")}', f'{title} vs Throughput',
                                  label1, label2)
            
            save_plot(fig, pdf, svg_dir, f'07_{metric.lower().replace(" ", "_").replace("-", "_")}_raw')
    
    # Normalized cache metrics (per packet)
    normalized_cache_metrics = [
        ('L1 I-cache misses per packet', 'L1 I-cache Misses per Packet'),
        ('L1 D-cache misses per packet', 'L1 D-cache Misses per Packet'),
        ('L1 I-TLB misses per packet', 'L1 I-TLB Misses per Packet'),
        ('L1 D-TLB misses per packet', 'L1 D-TLB Misses per Packet'),
        ('instructions per packet', 'Instructions per Packet'),
        ('Branch mis-pred per packet', 'Branch Mispredictions per Packet')
    ]
    
    # Plot normalized cache metrics
    for i, (metric, title) in enumerate(normalized_cache_metrics):
        if metric in df1.columns and metric in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            values1 = df1[metric]
            values2 = df2[metric]
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  metric.replace('per packet', '/ Packet'), f'{title} vs Throughput',
                                  label1, label2)
            
            save_plot(fig, pdf, svg_dir, f'08_{metric.lower().replace(" ", "_").replace("-", "_")}_normalized')

def plot_efficiency_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot efficiency metrics comparisons."""
    
    efficiency_metrics = [
        ('Cycles Per Packet', 'Cycles per Packet', True),
        ('instructions per packet', 'Instructions per Packet', True),
        ('Branch mis-pred per packet', 'Branch Mispredictions per Packet', True),
        ('Mean RTT (μs)', 'Mean Round-Trip Time (μs)', False)  # Use line plot for RTT trends
    ]
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    for i, (metric, title, use_bars) in enumerate(efficiency_metrics):
        if metric in df1.columns and metric in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            values1 = df1[metric]
            values2 = df2[metric]
            
            ylabel = title
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  ylabel, f'{title} vs Throughput',
                                  label1, label2, use_bars)
            
            save_plot(fig, pdf, svg_dir, f'09_{metric.lower().replace(" ", "_").replace("-", "_").replace("(μs)", "")}_efficiency')

def plot_packet_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2'):
    """Plot packet-related metrics comparisons."""
    
    packet_metrics = [
        ('Packet Rate (p/s)', 'Packet Rate (packets/s)', 1000),  # Convert to kpps
        ('Recv Thrput (Mb/s)', 'Received Throughput (Mb/s)', 1),
        ('Send Thrput (Mb/s)', 'Sent Throughput (Mb/s)', 1)
    ]
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    for i, (metric, title, divisor) in enumerate(packet_metrics):
        if metric in df1.columns and metric in df2.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            values1 = df1[metric] / divisor
            values2 = df2[metric] / divisor
            
            ylabel = title.replace('(packets/s)', '(Kpps)') if divisor == 1000 else title
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  ylabel, f'{title} vs Throughput',
                                  label1, label2)
            
            save_plot(fig, pdf, svg_dir, f'10_{metric.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}_packets')

def main():
    # Show usage if not enough arguments
    if len(sys.argv) < 3 and len(sys.argv) != 1:
        print("Usage: python plot_detailed_comparison.py <csv_file1> <csv_file2> [output_pdf] [label1] [label2]")
        print("Example: python plot_detailed_comparison.py baseline.csv optimized.csv comparison.pdf 'Baseline' 'Optimized'")
        return
    
    # Parse command line arguments
    if len(sys.argv) >= 3:
        csv_file1 = Path(sys.argv[1])
        csv_file2 = Path(sys.argv[2])
        output_file = Path(sys.argv[3] if len(sys.argv) > 3 else 'detailed_comparison_plots.pdf')
        label1 = sys.argv[4] if len(sys.argv) > 4 else 'DATA 1'
        label2 = sys.argv[5] if len(sys.argv) > 5 else 'DATA 2'
    else:
        # Default: use the same file twice for demonstration
        csv_file1 = Path('microkit_output_with_components.csv')
        csv_file2 = Path('microkit_output_with_components.csv')
        output_file = Path('detailed_comparison_plots.pdf')
        label1 = 'DATA 1'
        label2 = 'DATA 2'
    
    # Check if files exist
    if not csv_file1.exists():
        print(f"Error: {csv_file1} not found!")
        return
    if not csv_file2.exists():
        print(f"Error: {csv_file2} not found!")
        return
    
    print(f"Loading data from {csv_file1} and {csv_file2}...")
    df1 = load_data(csv_file1)
    df2 = load_data(csv_file2)
    
    # Create SVG directory alongside PDF
    svg_dir = output_file.parent / (output_file.stem + '_svgs')
    svg_dir.mkdir(exist_ok=True)
    
    # Create PDF with plots
    print(f"Generating detailed plots to {output_file}...")
    print(f"Generating SVG files to {svg_dir}/")
    with PdfPages(output_file) as pdf:
        # Instructions per second
        plot_instructions_per_second(pdf, svg_dir, df1, df2, label1, label2)
        
        # Throughput vs CPU utilization (special dual-axis plot)
        plot_throughput_vs_cpu(pdf, svg_dir, df1, df2, label1, label2)
        
        # Comprehensive CPU utilization (system + all components)
        plot_comprehensive_cpu_utilization(pdf, svg_dir, df1, df2, label1, label2)
        
        # CPU utilization
        plot_cpu_utilization(pdf, svg_dir, df1, df2, label1, label2)
        
        # Cache metrics
        plot_cache_metrics(pdf, svg_dir, df1, df2, label1, label2)
        
        # Efficiency metrics
        plot_efficiency_metrics(pdf, svg_dir, df1, df2, label1, label2)
        
        # Packet metrics
        plot_packet_metrics(pdf, svg_dir, df1, df2, label1, label2)
        
        # Add metadata to PDF
        d = pdf.infodict()
        d['Title'] = 'Detailed Performance Comparison Plots'
        d['Author'] = 'Performance Analysis Tool'
        d['Subject'] = 'Detailed Network Performance Metrics Comparison'
        d['Keywords'] = 'Performance, Instructions, CPU Utilization, Cache, Throughput'
    
    print(f"PDF saved to {output_file}")
    print(f"SVG files saved to {svg_dir}/")
    print("Detailed plot generation complete!")

if __name__ == "__main__":
    main()