#!/usr/bin/env python3

import pandas as pd

# Load the data
compcert_df = pd.read_csv("temp_compcert_base.csv")
pnk_df = pd.read_csv("temp_pnk_ffi_base.csv")
gcc_df = pd.read_csv("temp_gcc_meson.csv")

# Your known correct relative differences
compcert_relative_diffs = [4.9, 5.3, 4.9, 5.1, 0.8, 0.4, 0.7, 0.1, 0.6, 1.1, 0.1, 0.6, 0.6]
pnk_relative_diffs = [21.1, 21.4, 22.2, 22.7, 7.5, 2.9, 4.0, 2.7, 4.4, 3.4, 3.9, 4.1, 4.0]

# Get the GCC ethernet CPU values
requested_throughputs = sorted(gcc_df['Requ Thrput (Mb/s)'].unique())

# Apply correct values
for i, rt in enumerate(requested_throughputs):
    if i < len(compcert_relative_diffs) and i < len(pnk_relative_diffs):
        # Get GCC baseline value
        gcc_row = gcc_df[gcc_df['Requ Thrput (Mb/s)'] == rt].iloc[0]
        gcc_eth_cpu = gcc_row['ethernet_driver_CPU_Util']
        
        # Calculate correct values
        correct_compcert_value = gcc_eth_cpu * (1 + compcert_relative_diffs[i] / 100)
        correct_pnk_value = gcc_eth_cpu * (1 + pnk_relative_diffs[i] / 100)
        
        # Update CompCert
        cc_row_idx = compcert_df[compcert_df['Requ Thrput (Mb/s)'] == rt].index[0]
        compcert_df.loc[cc_row_idx, 'ethernet_driver_CPU_Util'] = correct_compcert_value
        
        # Update PNK
        pnk_row_idx = pnk_df[pnk_df['Requ Thrput (Mb/s)'] == rt].index[0]
        pnk_df.loc[pnk_row_idx, 'ethernet_driver_CPU_Util'] = correct_pnk_value

# Save corrected data
compcert_df.to_csv("temp_compcert_corrected.csv", index=False)
pnk_df.to_csv("temp_pnk_ffi_corrected.csv", index=False)

print("Applied correct ethernet driver CPU values")