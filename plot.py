#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import sys
from pathlib import Path
import os

plt.style.use('seaborn-v0_8-whitegrid')

plt.rcParams['font.family'] = 'monospace'
plt.rcParams['font.monospace'] = ['DejaVu Sans Mono', 'Consolas', 'Monaco', 'Courier New', 'monospace']

COLOR_BASELINE = '#84A5C7'
COLOR_COMPARATOR = '#F18484'
COLOR_DIFF_LINE = '#555555'

PRESENTATION_TITLE_SIZE = 24
PRESENTATION_AXIS_LABEL_SIZE = 20
PRESENTATION_LEGEND_SIZE = 18
PRESENTATION_DIFF_LABEL_SIZE = 16
PRESENTATION_VALUE_LABEL_SIZE = 16
PRESENTATION_LINE_WIDTH = 4
PRESENTATION_MARKER_SIZE = 12
PRESENTATION_DIFF_MARKER_SIZE = 14

REGULAR_TITLE_SIZE = 14
REGULAR_AXIS_LABEL_SIZE = 12
REGULAR_LEGEND_SIZE = 10
REGULAR_DIFF_LABEL_SIZE = 7
REGULAR_VALUE_LABEL_SIZE = 8
REGULAR_LINE_WIDTH = 2
REGULAR_MARKER_SIZE = 8
REGULAR_DIFF_MARKER_SIZE = 10

def load_data(csv_file):
    df = pd.read_csv(csv_file)
    df = df[df['Kernel Cycles'].notna()]
    df = df.reset_index(drop=True)
    
    return df

def calculate_relative_diff(baseline, comparison):
    return ((comparison - baseline) / baseline) * 100

def create_comparison_plot(ax1, ax2, x_positions, x_labels, y1, y2, ylabel, title, label1, label2, use_bars=True, show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    
    if presentation_mode:
        title_size = PRESENTATION_TITLE_SIZE
        axis_label_size = PRESENTATION_AXIS_LABEL_SIZE
        legend_size = PRESENTATION_LEGEND_SIZE
        diff_label_size = PRESENTATION_DIFF_LABEL_SIZE
        value_label_size = PRESENTATION_VALUE_LABEL_SIZE
        line_width = PRESENTATION_LINE_WIDTH
        marker_size = PRESENTATION_MARKER_SIZE
        diff_marker_size = PRESENTATION_DIFF_MARKER_SIZE
    else:
        title_size = REGULAR_TITLE_SIZE
        axis_label_size = REGULAR_AXIS_LABEL_SIZE
        legend_size = REGULAR_LEGEND_SIZE
        diff_label_size = REGULAR_DIFF_LABEL_SIZE
        value_label_size = REGULAR_VALUE_LABEL_SIZE
        line_width = REGULAR_LINE_WIDTH
        marker_size = REGULAR_MARKER_SIZE
        diff_marker_size = REGULAR_DIFF_MARKER_SIZE
    
    y1_displayed = np.array([float(f'{val:.1f}') if val >= 10 else float(f'{val:.2f}') for val in y1])
    y2_displayed = np.array([float(f'{val:.1f}') if val >= 10 else float(f'{val:.2f}') for val in y2])
    
    if use_bars:
        width = 0.35
        gap = 0.05
        x1 = np.array(x_positions) - width/2 - gap/2
        x2 = np.array(x_positions) + width/2 + gap/2
        
        bars1 = ax1.bar(x1, y1, width, label=label1, color=COLOR_BASELINE, alpha=0.85)
        bars2 = ax1.bar(x2, y2, width, label=label2, color=COLOR_COMPARATOR, alpha=0.85)
        
        if show_value_labels:
            for bar, val, disp_val in zip(bars1, y1, y1_displayed):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.03,
                        f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                        ha='center', va='bottom', fontsize=value_label_size, color=COLOR_BASELINE)
            
            for bar, val, disp_val in zip(bars2, y2, y2_displayed):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.03,
                        f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                        ha='center', va='bottom', fontsize=value_label_size, color=COLOR_COMPARATOR)
    else:
        ax1.plot(x_positions, y1, 'o-', label=label1, linewidth=line_width, markersize=marker_size, color=COLOR_BASELINE)
        ax1.plot(x_positions, y2, 's-', label=label2, linewidth=line_width, markersize=marker_size, color=COLOR_COMPARATOR)
        
        if show_value_labels:
            for x, val, disp_val in zip(x_positions, y1, y1_displayed):
                ax1.text(x, val + max(y1)*0.05, f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                        ha='center', va='bottom', fontsize=value_label_size, color=COLOR_BASELINE)
            
            for x, val, disp_val in zip(x_positions, y2, y2_displayed):
                ax1.text(x, val + max(y2)*0.05, f'{disp_val:.1f}' if val >= 10 else f'{disp_val:.2f}',
                        ha='center', va='bottom', fontsize=value_label_size, color=COLOR_COMPARATOR)
    
    ax1.set_ylabel(ylabel, fontsize=axis_label_size)
    ax1.set_title(title, fontsize=title_size, fontweight='bold')
    ax1.set_xlabel('Requested Throughput (Mb/s)', fontsize=axis_label_size)
    ax1.grid(True, alpha=0.3, linewidth=0.5, linestyle='-', which='major')
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(x_labels, rotation=45)
    
    rel_diff = calculate_relative_diff(y1_displayed, y2_displayed)
    
    if show_diff_overlay:
        ax_twin = ax1.twinx()
        
        ax_twin.plot(x_positions, rel_diff, color=COLOR_DIFF_LINE, linewidth=line_width, zorder=5)
        
        for x, diff in zip(x_positions, rel_diff):
            ax_twin.plot(x, diff, 'o', color=COLOR_DIFF_LINE, markersize=diff_marker_size, zorder=6)
            
            ax_twin.text(x, diff + 5, f'{diff:.1f}%', 
                        ha='center', va='bottom', fontsize=diff_label_size, 
                        color=COLOR_DIFF_LINE, fontweight='bold', zorder=7,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgray', alpha=0.7, edgecolor='gray', linewidth=0.5))
        
        ax_twin.set_ylim(-20, 80)
        ax_twin.set_ylabel('Relative Difference (%)', fontsize=axis_label_size)
        
        ax_twin.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7, zorder=3)
        
        ax_twin.grid(True, alpha=0.2, linewidth=0.5, linestyle='--', which='major', zorder=1)
        
        handles1, labels1 = ax1.get_legend_handles_labels()
        rel_line = plt.Line2D([0], [0], color='black', linewidth=2, 
                             marker='o', markersize=8, markerfacecolor='gray',
                             label=f'Relative Diff ({label2} vs {label1})')
        ax1.legend(handles1 + [rel_line], labels1 + [rel_line.get_label()], 
                  loc='upper left', fontsize=legend_size, framealpha=0.9)
    else:
        ax1.legend(loc='upper left', fontsize=legend_size, framealpha=0.9)
    
    if show_diff_subplot and ax2 is not None:
        colors = [COLOR_DIFF_LINE for x in rel_diff]
        bars = ax2.bar(x_positions, rel_diff, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        ax2.set_xlabel('Requested Throughput (Mb/s)', fontsize=12)
        ax2.set_ylabel('Relative Difference (%)', fontsize=12)
        ax2.set_title(f'Relative Difference ({label2} vs {label1} baseline)', fontsize=12)
        ax2.set_xticks(x_positions)
        ax2.set_xticklabels(x_labels, rotation=45)
        ax2.set_ylim(-20, 80)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.grid(True, alpha=0.3, linewidth=0.5, linestyle='-', axis='y', which='major')
        
        for bar, val in zip(bars, rel_diff):
            height = bar.get_height()
            color = COLOR_DIFF_LINE
            if abs(height) > 0.1:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{val:.1f}%', ha='center', 
                        va='bottom' if height >= 0 else 'top', 
                        fontsize=9, color=color, fontweight='bold')

def get_figure_size(presentation_mode, show_diff_subplot=False):
    """Get appropriate figure size based on mode and subplot configuration."""
    if presentation_mode:
        return (16, 16) if show_diff_subplot else (16, 12)
    else:
        return (12, 10) if show_diff_subplot else (12, 8)

def save_plot(fig, pdf, svg_dir, filename, presentation_mode=False):
    """Save plot to both PDF and SVG (if svg_dir provided)."""
    if presentation_mode:
        plt.tight_layout(pad=2.0)
    else:
        plt.tight_layout()
    pdf.savefig(fig)
    if svg_dir:
        plt.savefig(svg_dir / f'{filename}.svg', format='svg', bbox_inches='tight')
    plt.close()

def plot_instructions_per_second(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot instructions per second comparison."""
    
    figsize = get_figure_size(presentation_mode, show_diff_subplot)
    if show_diff_subplot:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=figsize)
        ax2 = None
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    inst_per_sec1 = df1['Instructions per Second'] / 1e9
    inst_per_sec2 = df2['Instructions per Second'] / 1e9
    
    create_comparison_plot(ax1, ax2, x_positions, x_labels, inst_per_sec1, inst_per_sec2,
                          'Instructions per Second (Billions)', 'Instructions per Second vs Throughput',
                          label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
    
    save_plot(fig, pdf, svg_dir, '01_instructions_per_second', presentation_mode)

def plot_throughput_vs_cpu(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', presentation_mode=False):
    """Plot requested vs received throughput with CPU utilization overlay."""
    
    figsize = get_figure_size(presentation_mode, False)
    fig, ax1 = plt.subplots(1, 1, figsize=figsize)
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    width = 0.35
    gap = 0.05  # Add small gap between bars
    x1 = np.array(x_positions) - width/2 - gap/2
    x2 = np.array(x_positions) + width/2 + gap/2
    
    bars1 = ax1.bar(x1, df1['Recv Thrput (Mb/s)'], width, label=f'{label1} Recv Throughput', 
                    color=COLOR_BASELINE, alpha=0.9)
    bars2 = ax1.bar(x2, df2['Recv Thrput (Mb/s)'], width, label=f'{label2} Recv Throughput', 
                    color=COLOR_COMPARATOR, alpha=0.9)
    
    
    if presentation_mode:
        title_size = PRESENTATION_TITLE_SIZE
        axis_label_size = PRESENTATION_AXIS_LABEL_SIZE
        legend_size = PRESENTATION_LEGEND_SIZE
        line_width = PRESENTATION_LINE_WIDTH
        marker_size = PRESENTATION_MARKER_SIZE
    else:
        title_size = REGULAR_TITLE_SIZE
        axis_label_size = REGULAR_AXIS_LABEL_SIZE
        legend_size = REGULAR_LEGEND_SIZE
        line_width = REGULAR_LINE_WIDTH
        marker_size = REGULAR_MARKER_SIZE
    
    ax1.set_xlabel('Requested Throughput (Mb/s)', fontsize=axis_label_size)
    ax1.set_ylabel('Received Throughput (Mb/s)', fontsize=axis_label_size)
    ax1.set_title('Received Throughput vs Requested with CPU Utilization Overlay', fontsize=title_size, fontweight='bold')
    ax1.grid(True, alpha=0.3, linewidth=0.5, linestyle='-', which='major')
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(x_labels, rotation=45)
    
    ax2 = ax1.twinx()
    cpu_util1 = df1['CPU Util (Fraction)'] * 100
    cpu_util2 = df2['CPU Util (Fraction)'] * 100
    
    line1 = ax2.plot(x_positions, cpu_util1, 'o', label=f'{label1} CPU Util', 
                     linewidth=line_width, markersize=marker_size, color=COLOR_DIFF_LINE, linestyle='-')
    line2 = ax2.plot(x_positions, cpu_util2, 's', label=f'{label2} CPU Util', 
                     linewidth=line_width, markersize=marker_size, color=COLOR_DIFF_LINE, linestyle='--')
    
    
    ax2.set_ylabel('CPU Utilization (%)', fontsize=axis_label_size)
    ax2.set_ylim(0, 105)
    ax2.grid(True, alpha=0.2, linewidth=0.5, linestyle='--', which='major')
    
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', fontsize=legend_size)
    
    save_plot(fig, pdf, svg_dir, '02_throughput_vs_cpu', presentation_mode)

def plot_comprehensive_cpu_utilization(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot comprehensive CPU utilization using standard format with Total System + components."""
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    total_util1 = df1['CPU Util (Fraction)'] * 100
    total_util2 = df2['CPU Util (Fraction)'] * 100
    
    figsize = get_figure_size(presentation_mode, show_diff_subplot)
    if show_diff_subplot:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=figsize)
        ax2 = None
    
    create_comparison_plot(ax1, ax2, x_positions, x_labels, total_util1, total_util2,
                          'CPU Utilization (%)', 'Total System CPU Utilization vs Throughput',
                          label1, label2, use_bars=True, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
    save_plot(fig, pdf, svg_dir, '03_total_cpu_utilization', presentation_mode)
    
    components = ['ethernet_driver', 'net_virt_tx', 'net_virt_rx', 'client0', 'client0_net_copier']
    component_names = ['Ethernet Driver CPU Utilization', 'Net Virt TX CPU Utilization', 
                       'Net Virt RX CPU Utilization', 'Client0 CPU Utilization', 'Client0 Net Copier CPU Utilization']
    
    for i, (component, name) in enumerate(zip(components, component_names)):
        cpu_col = f'{component}_CPU_Util'
        if cpu_col in df1.columns and cpu_col in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            util1 = df1[cpu_col]
            util2 = df2[cpu_col]
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, util1, util2,
                                  'CPU Utilization (%)', f'{name} vs Throughput',
                                  label1, label2, use_bars=True, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'04_{component}_utilization', presentation_mode)

def plot_cpu_utilization(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot CPU utilization comparison."""
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    figsize = get_figure_size(presentation_mode, show_diff_subplot)
    if show_diff_subplot:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=figsize)
        ax2 = None
    
    cpu_util1 = df1['CPU Util (Fraction)'] * 100
    cpu_util2 = df2['CPU Util (Fraction)'] * 100
    
    create_comparison_plot(ax1, ax2, x_positions, x_labels, cpu_util1, cpu_util2,
                          'CPU Utilization (%)', 'System CPU Utilization vs Throughput',
                          label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
    
    save_plot(fig, pdf, svg_dir, '05_system_cpu_utilization', presentation_mode)
    
    raw_cpu_metrics = [
        ('Total Cycles', 'Total CPU Cycles'),
        ('Kernel Cycles', 'Kernel CPU Cycles'),
        ('User Cycles', 'User CPU Cycles'),
        ('Idle Cycles', 'Idle CPU Cycles')
    ]
    
    for i, (metric, title) in enumerate(raw_cpu_metrics):
        if metric in df1.columns and metric in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            values1 = df1[metric] / 1e9
            values2 = df2[metric] / 1e9
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  f'{metric} (Billions)', f'{title} vs Throughput',
                                  label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'06_{metric.lower().replace(" ", "_")}_cycles', presentation_mode)

def plot_cache_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot cache metrics comparisons."""
    
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
    
    for i, (metric, title) in enumerate(raw_cache_metrics):
        if metric in df1.columns and metric in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            values1 = df1[metric] / 1e6
            values2 = df2[metric] / 1e6
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  f'{title.replace("(Total)", "(Millions)")}', f'{title} vs Throughput',
                                  label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'07_{metric.lower().replace(" ", "_").replace("-", "_")}_raw', presentation_mode)
    
    normalized_cache_metrics = [
        ('L1 I-cache misses per packet', 'L1 I-cache Misses per Packet'),
        ('L1 D-cache misses per packet', 'L1 D-cache Misses per Packet'),
        ('L1 I-TLB misses per packet', 'L1 I-TLB Misses per Packet'),
        ('L1 D-TLB misses per packet', 'L1 D-TLB Misses per Packet'),
        ('instructions per packet', 'Instructions per Packet'),
        ('Branch mis-pred per packet', 'Branch Mispredictions per Packet')
    ]
    
    for i, (metric, title) in enumerate(normalized_cache_metrics):
        if metric in df1.columns and metric in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            values1 = df1[metric]
            values2 = df2[metric]
            
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  metric.replace('per packet', '/ Packet'), f'{title} vs Throughput',
                                  label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'08_{metric.lower().replace(" ", "_").replace("-", "_")}_normalized', presentation_mode)

def plot_efficiency_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot efficiency metrics comparisons."""
    
    efficiency_metrics = [
        ('Cycles Per Packet', 'Cycles per Packet', True),
        ('instructions per packet', 'Instructions per Packet', True),
        ('Branch mis-pred per packet', 'Branch Mispredictions per Packet', True),
        ('Mean RTT (μs)', 'Mean Round-Trip Time (μs)', False)
    ]
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    for i, (metric, title, use_bars) in enumerate(efficiency_metrics):
        if metric in df1.columns and metric in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            values1 = df1[metric]
            values2 = df2[metric]
            
            ylabel = title
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  ylabel, f'{title} vs Throughput',
                                  label1, label2, use_bars, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'09_{metric.lower().replace(" ", "_").replace("-", "_").replace("(μs)", "")}_efficiency', presentation_mode)

def plot_packet_metrics(pdf, svg_dir, df1, df2, label1='Dataset 1', label2='Dataset 2', show_diff_overlay=True, show_diff_subplot=False, show_value_labels=False, presentation_mode=False):
    """Plot packet-related metrics comparisons."""
    
    packet_metrics = [
        ('Packet Rate (p/s)', 'Packet Rate (packets/s)', 1000),
        ('Recv Thrput (Mb/s)', 'Received Throughput (Mb/s)', 1),
        ('Send Thrput (Mb/s)', 'Sent Throughput (Mb/s)', 1)
    ]
    
    throughput = df1['Requ Thrput (Mb/s)']
    x_positions = range(len(throughput))
    x_labels = [f'{int(x)}' for x in throughput]
    
    for i, (metric, title, divisor) in enumerate(packet_metrics):
        if metric in df1.columns and metric in df2.columns:
            figsize = get_figure_size(presentation_mode, show_diff_subplot)
            if show_diff_subplot:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=figsize)
                ax2 = None
            
            values1 = df1[metric] / divisor
            values2 = df2[metric] / divisor
            
            ylabel = title.replace('(packets/s)', '(Kpps)') if divisor == 1000 else title
            create_comparison_plot(ax1, ax2, x_positions, x_labels, values1, values2,
                                  ylabel, f'{title} vs Throughput',
                                  label1, label2, show_diff_overlay=show_diff_overlay, show_diff_subplot=show_diff_subplot, show_value_labels=show_value_labels, presentation_mode=presentation_mode)
            
            save_plot(fig, pdf, svg_dir, f'10_{metric.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")}_packets', presentation_mode)

def main():
    if len(sys.argv) < 3 and len(sys.argv) != 1:
        print("Usage: python plot.py <csv_file1> <csv_file2> [output_pdf] [label1] [label2] [--no-diff-overlay] [--show-diff-subplot] [--show-value-labels] [--regular-mode]")
        print("Example: python plot.py baseline.csv optimized.csv comparison.pdf 'Baseline' 'Optimized'")
        print("Options:")
        print("  --no-diff-overlay    Don't show relative difference line overlay on main plots")
        print("  --show-diff-subplot  Show separate subplot for relative difference bars")
        print("  --show-value-labels  Show value labels on bars/points (default: off for cleaner look)")
        print("  --regular-mode       Use smaller fonts and thinner lines for detailed analysis (default: presentation mode)")
        return
    
    if len(sys.argv) >= 3:
        csv_file1 = Path(sys.argv[1])
        csv_file2 = Path(sys.argv[2])
        
        show_diff_overlay = '--no-diff-overlay' not in sys.argv
        show_diff_subplot = '--show-diff-subplot' in sys.argv
        show_value_labels = '--show-value-labels' in sys.argv
        presentation_mode = '--regular-mode' not in sys.argv
        
        args = [arg for arg in sys.argv if not arg.startswith('--')]
        
        output_file = Path(args[3] if len(args) > 3 else 'detailed_comparison_plots.pdf')
        label1 = args[4] if len(args) > 4 else 'DATA 1'
        label2 = args[5] if len(args) > 5 else 'DATA 2'
    else:
        csv_file1 = Path('microkit_output_with_components.csv')
        csv_file2 = Path('microkit_output_with_components.csv')
        output_file = Path('detailed_comparison_plots.pdf')
        label1 = 'DATA 1'
        label2 = 'DATA 2'
        show_diff_overlay = True
        show_diff_subplot = False
        show_value_labels = False
        presentation_mode = True
    
    if not csv_file1.exists():
        print(f"Error: {csv_file1} not found!")
        return
    if not csv_file2.exists():
        print(f"Error: {csv_file2} not found!")
        return
    
    df1 = load_data(csv_file1)
    df2 = load_data(csv_file2)
    
    svg_dir = output_file.parent / (output_file.stem + '_svgs')
    svg_dir.mkdir(exist_ok=True)
    
    with PdfPages(output_file) as pdf:
        plot_instructions_per_second(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        plot_throughput_vs_cpu(pdf, svg_dir, df1, df2, label1, label2, presentation_mode)
        
        plot_comprehensive_cpu_utilization(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        plot_cpu_utilization(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        plot_cache_metrics(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        plot_efficiency_metrics(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        plot_packet_metrics(pdf, svg_dir, df1, df2, label1, label2, show_diff_overlay, show_diff_subplot, show_value_labels, presentation_mode)
        
        d = pdf.infodict()
        d['Title'] = 'Detailed Performance Comparison Plots'
        d['Author'] = 'Performance Analysis Tool'
        d['Subject'] = 'Detailed Network Performance Metrics Comparison'
        d['Keywords'] = 'Performance, Instructions, CPU Utilization, Cache, Throughput'
    

if __name__ == "__main__":
    main()