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

# Use same sizing as plot.py (presentation mode)
PRESENTATION_TITLE_SIZE = 24
PRESENTATION_AXIS_LABEL_SIZE = 20
PRESENTATION_LEGEND_SIZE = 18
PRESENTATION_LINE_WIDTH = 4
PRESENTATION_MARKER_SIZE = 12

# Load data directly from CSV files
gcc_df = pd.read_csv("../sddf_benchmark/new_results/gcc_meson.csv")
compcert_df = pd.read_csv("../sddf_benchmark/new_results/compcert_meson.csv") 
pnk_df = pd.read_csv("../sddf_benchmark/new_results/pnk_meson_ffi.csv")

# Convert all datasets to consistent format
for df, name in [(gcc_df, 'GCC'), (compcert_df, 'CompCert'), (pnk_df, 'PNK')]:
    if 'Requested_Throughput' in df.columns:
        df['Requ Thrput (Mb/s)'] = df['Requested_Throughput'] / 1000000
        df['Recv Thrput (Mb/s)'] = df['Receive_Throughput'] / 1000000
        # Calculate CPU utilization from idle cycles
        df['CPU Util (%)'] = (1 - df['Idle_Cycles'] / df['Total_Cycles']) * 100

# Get unique requested throughputs and sort them
requested_throughputs = sorted(gcc_df['Requ Thrput (Mb/s)'].unique())

# Extract data for each dataset
gcc_recv_thrput = []
gcc_cpu_util = []
compcert_recv_thrput = []
compcert_cpu_util = []
pnk_recv_thrput = []
pnk_cpu_util = []

for rt in requested_throughputs:
    # GCC data
    gcc_row = gcc_df[gcc_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    gcc_recv_thrput.append(gcc_row['Recv Thrput (Mb/s)'])
    gcc_cpu_util.append(gcc_row['CPU Util (%)'])
    
    # CompCert data  
    cc_row = compcert_df[compcert_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    compcert_recv_thrput.append(cc_row['Recv Thrput (Mb/s)'])
    compcert_cpu_util.append(cc_row['CPU Util (%)'])
    
    # PNK data
    pnk_row = pnk_df[pnk_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
    pnk_recv_thrput.append(pnk_row['Recv Thrput (Mb/s)'])
    pnk_cpu_util.append(pnk_row['CPU Util (%)'])

# Create figure with twin y-axes (same size as plot.py presentation mode)
fig, ax1 = plt.subplots(figsize=(16, 12))
ax2 = ax1.twinx()

# Plot throughput on left axis
ax1.plot(requested_throughputs, gcc_recv_thrput, 
         color=COLOR_BASELINE, linewidth=PRESENTATION_LINE_WIDTH, marker='o', markersize=PRESENTATION_MARKER_SIZE, 
         label='C throughput', alpha=0.9)
ax1.plot(requested_throughputs, compcert_recv_thrput, 
         color=COLOR_COMPARATOR1, linewidth=PRESENTATION_LINE_WIDTH, marker='s', markersize=PRESENTATION_MARKER_SIZE, 
         label='CompCert C throughput', alpha=0.9)
ax1.plot(requested_throughputs, pnk_recv_thrput, 
         color=COLOR_COMPARATOR2, linewidth=PRESENTATION_LINE_WIDTH, marker='^', markersize=PRESENTATION_MARKER_SIZE, 
         label='Pancake throughput', alpha=0.9)

# Plot CPU utilization on right axis (dashed lines)
ax2.plot(requested_throughputs, gcc_cpu_util, 
         color=COLOR_BASELINE, linewidth=PRESENTATION_LINE_WIDTH, linestyle='--', marker='o', markersize=PRESENTATION_MARKER_SIZE, 
         label='C CPU util', alpha=0.7)
ax2.plot(requested_throughputs, compcert_cpu_util, 
         color=COLOR_COMPARATOR1, linewidth=PRESENTATION_LINE_WIDTH, linestyle='--', marker='s', markersize=PRESENTATION_MARKER_SIZE, 
         label='CompCert C CPU util', alpha=0.7)
ax2.plot(requested_throughputs, pnk_cpu_util, 
         color=COLOR_COMPARATOR2, linewidth=PRESENTATION_LINE_WIDTH, linestyle='--', marker='^', markersize=PRESENTATION_MARKER_SIZE, 
         label='Pancake CPU util', alpha=0.7)

# Set labels and formatting
ax1.set_xlabel('Requested Throughput (Mb/s)', fontsize=PRESENTATION_AXIS_LABEL_SIZE)
ax1.set_ylabel('Receive Throughput (Mb/s)', fontsize=PRESENTATION_AXIS_LABEL_SIZE, color='black')
ax2.set_ylabel('CPU Utilization (%)', fontsize=PRESENTATION_AXIS_LABEL_SIZE, color='gray')

ax1.set_title('Throughput and CPU Utilisation vs Requested Throughput', fontsize=PRESENTATION_TITLE_SIZE, fontweight='bold')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right', fontsize=PRESENTATION_LEGEND_SIZE)

ax1.grid(True, alpha=0.3)
plt.tight_layout(pad=2.0)

plt.savefig('final/three_way_throughput_cpu_twinx.svg', format='svg', bbox_inches='tight')
plt.savefig('final/three_way_throughput_cpu_twinx.pdf', format='pdf', bbox_inches='tight')
plt.close()

print("Three-way throughput + CPU utilization plot saved to final/ as SVG and PDF")
print(f"\nData Summary:")
print(f"Requested throughputs: {[int(x) for x in requested_throughputs]}")
print(f"GCC: {min(gcc_recv_thrput):.1f}-{max(gcc_recv_thrput):.1f} Mb/s, {min(gcc_cpu_util):.1f}-{max(gcc_cpu_util):.1f}% CPU")
print(f"CompCert: {min(compcert_recv_thrput):.1f}-{max(compcert_recv_thrput):.1f} Mb/s, {min(compcert_cpu_util):.1f}-{max(compcert_cpu_util):.1f}% CPU")
print(f"PNK: {min(pnk_recv_thrput):.1f}-{max(pnk_recv_thrput):.1f} Mb/s, {min(pnk_cpu_util):.1f}-{max(pnk_cpu_util):.1f}% CPU")