# Network Performance Analysis Pipeline

This repository contains tools for parsing and analyzing network performance benchmarking data with comprehensive visualization.

## Files Overview

### Input Data Files
- `c_overflow_iq_data.txt` - C Overflow configuration performance data (IQ format) 
- `c_overflow_processed_data.txt` - C Overflow configuration processed utilization data

### Scripts
- `parse.py` - Main data parser (converts raw text files to structured CSV)
- `plot.py` - Comprehensive plotting script with visualization  
- `run.sh` - Automated pipeline script for complete analysis workflow

## Quick Start

### Option 1: Complete Pipeline (Recommended)

```bash
# Run complete pipeline with two dataset pairs for comparison
./run.sh config1_iq.txt config1_processed.txt config2_iq.txt config2_processed.txt output_dir

# Use same dataset twice for single-configuration analysis in comparison format
./run.sh c_overflow_iq_data.txt c_overflow_processed_data.txt c_overflow_iq_data.txt c_overflow_processed_data.txt results

# Custom dataset names  
./run.sh data1_iq.txt data1_proc.txt data2_iq.txt data2_proc.txt results "Baseline" "Optimized"
```

### Option 2: Manual Steps

#### Step 1: Parse Raw Data to CSV

```bash
# Parse C Overflow configuration  
python parse.py c_overflow_iq_data.txt c_overflow_processed_data.txt c_overflow_data.csv
```

#### Step 2: Generate Analysis Reports

```bash
# Generate individual configuration analysis (single dataset)
python plot.py c_overflow_data.csv c_overflow_data.csv c_overflow_analysis.pdf "C Overflow" "C Overflow"

# Generate comparison analysis (two datasets - example with hypothetical second dataset)
python plot.py c_overflow_data.csv other_config_data.csv config_comparison.pdf "C Overflow" "Other Config"
```

## Script Usage Details

### run.sh

**Purpose**: Complete automated pipeline for network performance analysis

**Usage**:
```bash
./run.sh <iq_file1> <processed_file1> <iq_file2> <processed_file2> [output_dir] [dataset1_name] [dataset2_name]
```

**Arguments**:
- `iq_file1`: First dataset IQ file (performance data)
- `processed_file1`: First dataset processed file (utilization data)
- `iq_file2`: Second dataset IQ file (performance data)  
- `processed_file2`: Second dataset processed file (utilization data)
- `output_dir`: Output directory (default: output)
- `dataset1_name`: First dataset label (default: extracted from filename)
- `dataset2_name`: Second dataset label (default: extracted from filename)

**Output**:
- `output_dir/dataset1_name_data.csv` - First dataset structured data
- `output_dir/dataset2_name_data.csv` - Second dataset structured data
- `output_dir/comparison_analysis.pdf` - Comprehensive comparison analysis

**Features**:
- Automatic dataset name extraction from filenames
- Parallel processing of both datasets
- Complete error handling and validation
- Colored terminal output with progress tracking
- Comprehensive analysis pipeline in one command

### parse.py

**Purpose**: Converts raw performance data files into structured CSV format

**Usage**:
```bash
python parse.py <iq_file> <processed_file> <output_csv>
```

**Arguments**:
- `iq_file`: Performance data file (throughput, RTT, packet stats)
- `processed_file`: Utilization data file (CPU cycles, hardware counters, component utilization)  
- `output_csv`: Output CSV file with combined structured data

**Output CSV Contains**:
- Throughput metrics (requested, received, sent)
- RTT statistics (min, mean, max, stdev, median)
- CPU utilization (total system + per-component)
- Hardware counters (cache misses, instructions, branch mispredictions)
- Derived metrics (per-packet values, instructions per second)
- Component-specific CPU utilization for: ethernet_driver, net_virt_tx, net_virt_rx, client0, client0_net_copier

### plot.py

**Purpose**: Generates comprehensive performance analysis with professional visualizations

**Usage**:
```bash
python plot.py <csv_file1> <csv_file2> <output_pdf> <label1> <label2>
```

**Arguments**:
- `csv_file1`: First dataset CSV (use same file twice for single-dataset analysis)
- `csv_file2`: Second dataset CSV  
- `output_pdf`: Output PDF file
- `label1`: Display label for first dataset
- `label2`: Display label for second dataset

**Generated Plots Include**:
- Instructions per second analysis
- Dual-axis throughput vs CPU utilization plot
- Total system CPU utilization analysis
- Individual component CPU utilization (5 components)
- CPU cycle metrics (total, kernel, user, idle)
- Cache performance metrics (raw and per-packet normalized)
- Efficiency metrics (cycles per packet, instructions per packet)
- Packet-level performance metrics

**Plot Format**:
- Standard top/bottom layout: raw comparison (top) + relative differences (bottom)
- Professional color scheme with clear legends
- All 13 test iterations displayed (10-1000 Mb/s)
- Bar charts for discrete comparisons, line plots for trends

## Example Workflows

### Analyze Single Configuration
```bash
# 1. Parse data
python parse.py c_overflow_iq_data.txt c_overflow_processed_data.txt my_data.csv

# 2. Generate comprehensive analysis  
python plot.py my_data.csv my_data.csv analysis_report.pdf "Configuration" "Configuration"
```

### Compare Two Configurations
```bash
# 1. Parse both datasets
python parse.py config1_iq.txt config1_processed.txt config1.csv
python parse.py config2_iq.txt config2_processed.txt config2.csv

# 2. Generate comparison
python plot.py config1.csv config2.csv comparison.pdf "Baseline" "Optimized"
```

## Key Features

- **Automatic data filtering**: Removes incomplete test records
- **Component-level analysis**: Tracks CPU utilization for individual system components
- **Comprehensive metrics**: 40+ performance indicators per test iteration
- **Professional visualization**: Publication-ready plots with consistent formatting
- **Flexible comparison**: Single dataset analysis or cross-configuration comparison
- **Accurate calculations**: Instructions per second uses total time (including warm-up/cool-down)

## Requirements

- Python 3.x
- pandas
- matplotlib  
- numpy

## Notes

- All calculations use 200,000 fixed packet count per test
- Packet size is 1472 bytes + 56 bytes overhead
- Test duration includes 10s warm-up and 10s cool-down periods
- Instructions per second calculated using total time (not just test duration)
- Component CPU utilization data parsed from processed files when available