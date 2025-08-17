#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Apply the same style and font settings as plot.py
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'monospace'
plt.rcParams['font.monospace'] = ['DejaVu Sans Mono', 'Consolas', 'Monaco', 'Courier New', 'monospace']

COLOR_BASELINE = '#84A5C7'     # Blue for GCC
COLOR_COMPARATOR1 = '#F18484'  # Red for CompCert  
COLOR_COMPARATOR2 = '#8BC34A'  # Soft green for PNK
COLOR_DIFF_LINE = '#555555'    # Gray for diff lines

# Use same sizing as plot.py (presentation mode)
PRESENTATION_TITLE_SIZE = 24
PRESENTATION_AXIS_LABEL_SIZE = 20
PRESENTATION_LEGEND_SIZE = 18
PRESENTATION_LINE_WIDTH = 4
PRESENTATION_MARKER_SIZE = 12
PRESENTATION_DIFF_MARKER_SIZE = 14

def calculate_relative_diff(baseline, comparison):
    """Calculate relative difference as percentage."""
    return ((comparison - baseline) / baseline) * 100

# Load data from temp CSV files (which have ethernet driver data)
gcc_df = pd.read_csv("temp_gcc_meson.csv")
compcert_df = pd.read_csv("temp_compcert_corrected.csv")  # Use corrected CompCert data
pnk_df = pd.read_csv("temp_pnk_ffi_corrected.csv")  # Use corrected PNK data

# Get unique requested throughputs and sort them
requested_throughputs = sorted(gcc_df['Requ Thrput (Mb/s)'].unique())
x_positions = range(len(requested_throughputs))
x_labels = [f'{int(rt)}' for rt in requested_throughputs]

# Extract ethernet driver CPU utilization for each dataset
gcc_eth_cpu = []
compcert_eth_cpu = []
pnk_eth_cpu = []

for rt in requested_throughputs:
    # GCC data (baseline)
    gcc_row = gcc_df[gcc_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    gcc_eth_cpu.append(gcc_row['ethernet_driver_CPU_Util'])
    
    # CompCert data (comparator 1)
    cc_row = compcert_df[compcert_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    compcert_eth_cpu.append(cc_row['ethernet_driver_CPU_Util'])
    
    # PNK data (comparator 2)
    pnk_row = pnk_df[pnk_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    pnk_eth_cpu.append(pnk_row['ethernet_driver_CPU_Util'])

# Calculate relative differences vs GCC baseline
compcert_diff = [calculate_relative_diff(gcc, cc) for gcc, cc in zip(gcc_eth_cpu, compcert_eth_cpu)]
pnk_diff = [calculate_relative_diff(gcc, pnk) for gcc, pnk in zip(gcc_eth_cpu, pnk_eth_cpu)]

# Create figure with twin y-axes (presentation mode size)
fig, ax1 = plt.subplots(figsize=(16, 12))
ax2 = ax1.twinx()

# Create three-way bar chart
width = 0.25
gap = 0.02
x1 = np.array(x_positions) - width - gap
x2 = np.array(x_positions)
x3 = np.array(x_positions) + width + gap

bars1 = ax1.bar(x1, gcc_eth_cpu, width, label='C', color=COLOR_BASELINE, alpha=0.85)
bars2 = ax1.bar(x2, compcert_eth_cpu, width, label='CompCert C', color=COLOR_COMPARATOR1, alpha=0.85)
bars3 = ax1.bar(x3, pnk_eth_cpu, width, label='Pancake', color=COLOR_COMPARATOR2, alpha=0.85)

# Plot relative difference lines on secondary y-axis
ax2.plot(x_positions, compcert_diff, 'o-', 
         color=COLOR_DIFF_LINE, linewidth=PRESENTATION_LINE_WIDTH, 
         markersize=PRESENTATION_DIFF_MARKER_SIZE, label='CompCert C vs C (%)', alpha=0.8)
ax2.plot(x_positions, pnk_diff, 
         color=COLOR_DIFF_LINE, linewidth=PRESENTATION_LINE_WIDTH, 
         markersize=PRESENTATION_DIFF_MARKER_SIZE, label='Pancake vs C (%)', alpha=0.8, linestyle='--', marker='s')

# Add horizontal line at 0% difference
ax2.axhline(y=0, color=COLOR_DIFF_LINE, linestyle=':', alpha=0.5, linewidth=2)

# Add value labels to difference lines (like in plot.py)
PRESENTATION_DIFF_LABEL_SIZE = 16
# CompCert labels go below the line
for x, val in zip(x_positions, compcert_diff):
    ax2.text(x, val - 5, f'{val:.1f}%', 
            ha='center', va='top', fontsize=PRESENTATION_DIFF_LABEL_SIZE, 
            color=COLOR_DIFF_LINE, fontweight='bold', zorder=7,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.7, edgecolor='gray', linewidth=0.5))

# PNK labels go above the line
for x, val in zip(x_positions, pnk_diff):
    ax2.text(x, val + 5, f'{val:.1f}%',
            ha='center', va='bottom', fontsize=PRESENTATION_DIFF_LABEL_SIZE, 
            color=COLOR_DIFF_LINE, fontweight='bold', zorder=7,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.7, edgecolor='gray', linewidth=0.5))

# Set labels and formatting
ax1.set_xlabel('Requested Throughput (Mb/s)', fontsize=PRESENTATION_AXIS_LABEL_SIZE)
ax1.set_ylabel('Ethernet Driver CPU Utilization (%)', fontsize=PRESENTATION_AXIS_LABEL_SIZE, color='black')
ax2.set_ylabel('Relative Difference from GCC (%)', fontsize=PRESENTATION_AXIS_LABEL_SIZE, color=COLOR_DIFF_LINE)

# Set right y-axis scale to match plot.py (-20 to 80)
ax2.set_ylim(-20, 80)

ax1.set_title('CPU Utilisation and Relative Overhead vs. Throughput', fontsize=PRESENTATION_TITLE_SIZE, fontweight='bold')

# Set x-axis
ax1.set_xticks(x_positions)
ax1.set_xticklabels(x_labels, rotation=45, ha='right')

# Combine legends
bars_handles = [bars1, bars2, bars3]
bars_labels = ['C', 'CompCert C', 'Pancake']
lines_handles, lines_labels = ax2.get_legend_handles_labels()

ax1.legend(bars_handles + lines_handles, bars_labels + lines_labels, 
          loc='upper left', fontsize=PRESENTATION_LEGEND_SIZE)

ax1.grid(True, alpha=0.3)
plt.tight_layout(pad=2.0)

plt.savefig('final/three_way_ethernet_cpu_bars_diff.svg', format='svg', bbox_inches='tight')
plt.savefig('final/three_way_ethernet_cpu_bars_diff.pdf', format='pdf', bbox_inches='tight')
plt.close()

print("Three-way ethernet driver CPU utilization plot saved to final/ as SVG and PDF")
print(f"\nData Summary:")
print(f"Requested throughputs: {[int(x) for x in requested_throughputs]}")
print(f"GCC ethernet CPU: {min(gcc_eth_cpu):.1f}-{max(gcc_eth_cpu):.1f}%")
print(f"CompCert ethernet CPU: {min(compcert_eth_cpu):.1f}-{max(compcert_eth_cpu):.1f}%")
print(f"PNK ethernet CPU: {min(pnk_eth_cpu):.1f}-{max(pnk_eth_cpu):.1f}%")
print(f"CompCert vs GCC diff: {min(compcert_diff):.1f}% to {max(compcert_diff):.1f}%")
print(f"PNK vs GCC diff: {min(pnk_diff):.1f}% to {max(pnk_diff):.1f}%")