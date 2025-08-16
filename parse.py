#!/usr/bin/env python3

import csv
import re
from pathlib import Path
import sys


def parse_iq_file(file_path):
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    summary_start = content.find('Result Summary:')
    if summary_start == -1:
        pattern = r'Requested_Throughput,Receive_Throughput,Send_Throughput,Packet_Size,Minimum_RTT,Average_RTT,Maximum_RTT,Stdev_RTT,Median_RTT,Bad_Packets,Idle_Cycles,Total_Cycles\n\s*(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),([\d.]+),(\d+),(\d+),(\d+),(\d+)'
        matches = re.findall(pattern, content)
    else:
        summary_content = content[summary_start:]
        pattern = r'Requested_Throughput,Receive_Throughput,Send_Throughput,Packet_Size,Minimum_RTT,Average_RTT,Maximum_RTT,Stdev_RTT,Median_RTT,Bad_Packets,Idle_Cycles,Total_Cycles\n((?:\d+,\d+,\d+,\d+,\d+,\d+,\d+,[\d.]+,\d+,\d+,\d+,\d+\n?)+)'
        
        summary_match = re.search(pattern, summary_content)
        if summary_match:
            summary_lines = summary_match.group(1).strip().split('\n')
            matches = []
            for line in summary_lines:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 12:
                        matches.append(tuple(parts[:12]))
        else:
            matches = []
    
    test_results = []
    for match in matches:
        result = {
            'Requ Thrput (Mb/s)': int(match[0]) / 1000000,
            'Recv Thrput (Mb/s)': int(match[1]) / 1000000,
            'Send Thrput (Mb/s)': int(match[2]) / 1000000,
            'Packet Size (bytes)': int(match[3]),
            'Min RTT (μs)': int(match[4]),
            'Mean RTT (μs)': int(match[5]),
            'Max RTT (μs)': int(match[6]),
            'RTT stdev (μs)': float(match[7]),
            'Med RTT (μs)': int(match[8]),
            'Bad Packets': int(match[9]),
            'Idle Cycles': int(match[10]),
            'Total Cycles': int(match[11])
        }
        test_results.append(result)
    
    return test_results


def parse_out_file(file_path):
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    test_data = []
    
    if any('System Total' in line and 'Core Cycles' in lines[0] for line in lines):
        system_totals = {}
        for line in lines:
            if line.startswith('System Total'):
                parts = line.strip().split(',')
                if len(parts) > 1:
                    throughput = parts[0].replace('System Total ', '')
                    system_totals[throughput] = {
                        'Core Cycles': int(parts[1]),
                        'System Cycles': int(parts[2]),
                        'Kernel Cycles': int(parts[3]),
                        'User Cycles': int(parts[4]),
                        'Kernel Entries': int(parts[5]),
                        'Schedules': int(parts[6])
                    }
        
        hw_data = []
        hw_section_found = False
        for i, line in enumerate(lines):
            if 'L1 i-cache misses' in line and 'L1 d-cache misses' in line:
                hw_section_found = True
                for j in range(i+1, len(lines)):
                    if lines[j].strip():
                        parts = lines[j].strip().split(',')
                        if len(parts) >= 6:
                            hw_data.append({
                                'L1 I-cache misses': int(parts[0]) if parts[0] else 0,
                                'L1 D-cache misses': int(parts[1]) if parts[1] else 0,
                                'L1 I-TLB misses': int(parts[2]) if parts[2] else 0,
                                'L1 D-TLB misses': int(parts[3]) if parts[3] else 0,
                                'Instructions': int(parts[4]) if parts[4] else 0,
                                'Branch mispredictions': int(parts[5]) if parts[5] else 0
                            })
                break
        
        component_data = {}
        current_test_idx = -1
        components_of_interest = ['ethernet_driver', 'net_virt_tx', 'net_virt_rx', 'client0', 'client0_net_copier']
        
        for line in lines:
            if line.startswith('TEST'):
                current_test_idx += 1
                if current_test_idx not in component_data:
                    component_data[current_test_idx] = {}
            
            for component in components_of_interest:
                if line.startswith(component + ','):
                    parts = line.strip().split(',')
                    if len(parts) >= 9:
                        if current_test_idx not in component_data:
                            component_data[current_test_idx] = {}
                        component_data[current_test_idx][component] = {
                            'CPU_Util': float(parts[7]),
                            'Kernel_Util': float(parts[8]),
                            'User_Util': float(parts[9]) if len(parts) > 9 else 0.0
                        }
        
        test_order = ['10Mb/s', '20Mb/s', '50Mb/s', '100Mb/s', '200Mb/s', 
                      '300Mb/s', '400Mb/s', '500Mb/s', '600Mb/s', '700Mb/s', 
                      '800Mb/s', '900Mb/s', '1000Mb/s']
        
        for i, throughput in enumerate(test_order):
            if throughput in system_totals:
                data = system_totals[throughput].copy()
                
                if i < len(hw_data):
                    data.update(hw_data[i])
                
                if i in component_data:
                    for component, comp_data in component_data[i].items():
                        data[f'{component}_CPU_Util'] = comp_data['CPU_Util']
                        data[f'{component}_Kernel_Util'] = comp_data['Kernel_Util']
                        data[f'{component}_User_Util'] = comp_data['User_Util']
                
                test_data.append(data)
    else:
        hw_pattern = r'\{[\s\n]*L1 i-cache misses:\s*(\d+)[\s\n]*L1 d-cache misses:\s*(\d+)[\s\n]*L1 i-tlb misses:\s*(\d+)[\s\n]*L1 d-tlb misses:\s*(\d+)[\s\n]*Instructions:\s*(\d+)[\s\n]*Branch mispredictions:\s*(\d+)[\s\n]*\}'
        
        hw_matches = re.findall(hw_pattern, content)
        
        util_pattern = r'Total utilisation details:[\s\n]*\{[\s\n]*KernelUtilisation:\s*(\d+)[\s\n]*KernelEntries:\s*(\d+)[\s\n]*NumberSchedules:\s*(\d+)[\s\n]*TotalUtilisation:\s*(\d+)'
        
        util_matches = re.findall(util_pattern, content)
        
        for i in range(min(len(hw_matches), len(util_matches))):
            data = {
                'L1 I-cache misses': int(hw_matches[i][0]),
                'L1 D-cache misses': int(hw_matches[i][1]),
                'L1 I-TLB misses': int(hw_matches[i][2]),
                'L1 D-TLB misses': int(hw_matches[i][3]),
                'Instructions': int(hw_matches[i][4]),
                'Branch mispredictions': int(hw_matches[i][5]),
                'Kernel Cycles': int(util_matches[i][0]),
                'Kernel Entries': int(util_matches[i][1]),
                'Schedules': int(util_matches[i][2]),
                'Core Cycles': int(util_matches[i][3]),
                'User Cycles': 0
            }
            test_data.append(data)
    
    return test_data


def combine_data(iq_results, out_data):
    
    combined_data = []
    
    for i in range(len(iq_results)):
        row = iq_results[i].copy()
        
        if i < len(out_data):
            for key, value in out_data[i].items():
                if key not in row:
                    row[key] = value
        
        if 'Core Cycles' in row and 'Total Cycles' not in row:
            row['Total Cycles'] = row['Core Cycles']
        
        if 'Total Cycles' in row and 'Idle Cycles' in row and row.get('Total Cycles', 0) > 0:
            idle_fraction = row['Idle Cycles'] / row['Total Cycles']
            row['CPU Util (Fraction)'] = round(1 - idle_fraction, 4)
        else:
            row['CPU Util (Fraction)'] = 'NA'
        
        if 'User Cycles' not in row or row['User Cycles'] == 0:
            if row.get('Total Cycles', 0) > 0 and row.get('Kernel Cycles', 0) > 0:
                row['User Cycles'] = row['Total Cycles'] - row['Kernel Cycles'] - row['Idle Cycles']
        
        total_packets = 200000
        row['Total Packets'] = total_packets
        row['Packets Sent'] = total_packets
        
        throughput_mbps = row['Recv Thrput (Mb/s)']
        packet_size = row['Packet Size (bytes)']
        packet_rate = (throughput_mbps * 1000000) / ((packet_size + 56) * 8)
        row['Packet Rate (p/s)'] = round(packet_rate, 2)
        
        if total_packets > 0:
            row['Cycles Per Packet'] = int(row['Total Cycles'] / total_packets) if 'Total Cycles' in row else 'NA'
            row['User cycles per packet'] = int(row['User Cycles'] / total_packets) if 'User Cycles' in row and row['User Cycles'] > 0 else 'NA'
            row['Kernel cycles per packet'] = int(row['Kernel Cycles'] / total_packets) if 'Kernel Cycles' in row else 'NA'
            row['Kernel entries per packet'] = round(row['Kernel Entries'] / total_packets, 2) if 'Kernel Entries' in row else 'NA'
            row['L1 I-cache misses per packet'] = round(row['L1 I-cache misses'] / total_packets, 2) if 'L1 I-cache misses' in row else 'NA'
            row['L1 D-cache misses per packet'] = round(row['L1 D-cache misses'] / total_packets, 2) if 'L1 D-cache misses' in row else 'NA'
            row['L1 I-TLB misses per packet'] = round(row['L1 I-TLB misses'] / total_packets, 2) if 'L1 I-TLB misses' in row else 'NA'
            row['L1 D-TLB misses per packet'] = round(row['L1 D-TLB misses'] / total_packets, 2) if 'L1 D-TLB misses' in row else 'NA'
            row['instructions per packet'] = int(row['Instructions'] / total_packets) if 'Instructions' in row else 'NA'
            row['Branch mis-pred per packet'] = round(row['Branch mispredictions'] / total_packets, 2) if 'Branch mispredictions' in row else 'NA'
        else:
            row['Cycles Per Packet'] = 'NA'
            row['User cycles per packet'] = 'NA'
            row['Kernel cycles per packet'] = 'NA'
            row['Kernel entries per packet'] = 'NA'
            row['L1 I-cache misses per packet'] = 'NA'
            row['L1 D-cache misses per packet'] = 'NA'
            row['L1 I-TLB misses per packet'] = 'NA'
            row['L1 D-TLB misses per packet'] = 'NA'
            row['instructions per packet'] = 'NA'
            row['Branch mis-pred per packet'] = 'NA'
        
        row['Warm-up (s)'] = 10
        row['Cool-down (s)'] = 10
        
        if packet_rate > 0:
            test_duration = total_packets / packet_rate
            row['Test Duration (s)'] = round(test_duration, 2)
            row['Total Time (s)'] = round(test_duration + 10 + 10, 2)
            
            total_time = test_duration + 10 + 10
            if 'Instructions' in row and row['Instructions'] > 0:
                instructions_per_sec = row['Instructions'] / total_time
                row['Instructions per Second'] = int(instructions_per_sec)
            else:
                row['Instructions per Second'] = 'NA'
        else:
            row['Test Duration (s)'] = 'NA'
            row['Total Time (s)'] = 'NA'
            row['Instructions per Second'] = 'NA'
        
        combined_data.append(row)
    
    return combined_data


def write_csv(data_rows, output_file):
    
    base_columns = [
        'Requ Thrput (Mb/s)', 'Recv Thrput (Mb/s)', 'Send Thrput (Mb/s)',
        'Packet Size (bytes)', 'Min RTT (μs)', 'Mean RTT (μs)', 'Max RTT (μs)',
        'RTT stdev (μs)', 'Med RTT (μs)', 'Idle Cycles', 'Total Cycles',
        'CPU Util (Fraction)', 'Kernel Cycles', 'User Cycles', 'Kernel Entries',
        'Schedules', 'Warm-up (s)', 'Cool-down (s)', 'Test Duration (s)', 
        'Total Time (s)', 'Packets Sent', 'Packet Rate (p/s)', 'Total Packets', 
        'L1 I-cache misses', 'L1 D-cache misses', 'L1 I-TLB misses', 'L1 D-TLB misses',
        'Instructions', 'Instructions per Second', 'Branch mispredictions', 
        'Cycles Per Packet', 'User cycles per packet', 'Kernel cycles per packet',
        'Kernel entries per packet', 'L1 I-cache misses per packet',
        'L1 D-cache misses per packet', 'L1 I-TLB misses per packet',
        'L1 D-TLB misses per packet', 'instructions per packet',
        'Branch mis-pred per packet'
    ]
    
    all_keys = set()
    for row in data_rows:
        all_keys.update(row.keys())
    
    component_columns = sorted([k for k in all_keys if k not in base_columns])
    columns = base_columns + component_columns
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for row in data_rows:
            for col in columns:
                if col not in row:
                    row[col] = 'NA'
            writer.writerow(row)
    
    print(f"CSV file written to: {output_file}")


def main():
    
    if len(sys.argv) > 2:
        iq_file = Path(sys.argv[1])
        out_file = Path(sys.argv[2])
        output_file = Path(sys.argv[3] if len(sys.argv) > 3 else 'microkit_output.csv')
    else:
        iq_file = Path('pnk_microkit_iq_v1.txt')
        out_file = Path('pnk_microkit_out_v1.txt')
        output_file = Path('microkit_output.csv')
    
    if not iq_file.exists():
        print(f"Error: {iq_file} not found!")
        return
    
    if not out_file.exists():
        print(f"Error: {out_file} not found!")
        return
    
    iq_results = parse_iq_file(iq_file)
    
    seen_throughputs = set()
    unique_results = []
    duplicates_removed = 0
    
    for result in iq_results:
        throughput = result['Requ Thrput (Mb/s)']
        if throughput not in seen_throughputs:
            seen_throughputs.add(throughput)
            unique_results.append(result)
        else:
            duplicates_removed += 1
    
    iq_results = unique_results
    
    out_data = parse_out_file(out_file)
    
    combined_data = combine_data(iq_results, out_data)
    
    write_csv(combined_data, output_file)
    


if __name__ == "__main__":
    main()