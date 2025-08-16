// Color scheme matching plot.py
const COLOR_BASELINE = '#84A5C7';
const COLOR_COMPARATOR = '#F18484';
const COLOR_DIFF_LINE = '#555555';

// Chart configuration
let charts = [];
let csimData = null;
let pnkData = null;

// Load CSV data
async function loadData() {
    try {
        // Clear existing charts
        charts.forEach(chart => chart.destroy());
        charts = [];
        
        document.getElementById('chartGrid').innerHTML = '<div class="loading">Loading data...</div>';
        
        // Load both CSV files
        const csimResponse = await fetch('csim_data.csv');
        const pnkResponse = await fetch('pnk_data.csv');
        
        const csimText = await csimResponse.text();
        const pnkText = await pnkResponse.text();
        
        // Parse CSV data
        csimData = Papa.parse(csimText, { header: true, dynamicTyping: true }).data;
        pnkData = Papa.parse(pnkText, { header: true, dynamicTyping: true }).data;
        
        // Filter out incomplete records
        csimData = csimData.filter(row => row['Kernel Cycles'] !== null && row['Kernel Cycles'] !== undefined);
        pnkData = pnkData.filter(row => row['Kernel Cycles'] !== null && row['Kernel Cycles'] !== undefined);
        
        console.log(`Loaded ${csimData.length} C SIM records and ${pnkData.length} PNK records`);
        
        // Create visualizations based on selected metric
        updateVisualizations();
        
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('chartGrid').innerHTML = '<div class="loading">Error loading data. Please check if CSV files are available.</div>';
    }
}

// Calculate relative difference
function calculateRelativeDiff(baseline, comparison) {
    return baseline.map((val, i) => ((comparison[i] - val) / val) * 100);
}

// Update visualizations based on selected metric
function updateVisualizations() {
    const selectedMetric = document.getElementById('metricSelect').value;
    const showDiff = document.getElementById('diffToggle').checked;
    const presentationMode = document.getElementById('presentationMode').checked;
    
    // Clear chart grid
    document.getElementById('chartGrid').innerHTML = '';
    charts = [];
    
    switch(selectedMetric) {
        case 'instructions':
            createInstructionsChart(showDiff, presentationMode);
            break;
        case 'cpu':
            createCPUChart(showDiff, presentationMode);
            break;
        case 'throughput':
            createThroughputVsCPUChart(presentationMode);
            break;
        case 'cycles':
            createCyclesCharts(showDiff, presentationMode);
            break;
        case 'cache':
            createCacheCharts(showDiff, presentationMode);
            break;
        case 'efficiency':
            createEfficiencyCharts(showDiff, presentationMode);
            break;
        case 'packets':
            createPacketCharts(showDiff, presentationMode);
            break;
        case 'components':
            createComponentCharts(showDiff, presentationMode);
            break;
    }
}

// Create a chart container
function createChartContainer(title) {
    const container = document.createElement('div');
    container.className = 'chart-container';
    
    const titleElement = document.createElement('div');
    titleElement.className = 'chart-title';
    titleElement.textContent = title;
    container.appendChild(titleElement);
    
    const wrapper = document.createElement('div');
    wrapper.className = 'chart-wrapper';
    
    const canvas = document.createElement('canvas');
    wrapper.appendChild(canvas);
    container.appendChild(wrapper);
    
    document.getElementById('chartGrid').appendChild(container);
    
    return canvas;
}

// Get chart font sizes based on mode
function getFontSizes(presentationMode) {
    return presentationMode ? {
        title: 24,
        axisLabel: 20,
        legend: 18,
        ticks: 16
    } : {
        title: 14,
        axisLabel: 12,
        legend: 10,
        ticks: 10
    };
}

// Create Instructions per Second chart
function createInstructionsChart(showDiff, presentationMode) {
    const canvas = createChartContainer('Instructions per Second vs Throughput');
    const ctx = canvas.getContext('2d');
    const fonts = getFontSizes(presentationMode);
    
    const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
    const csimInstructions = csimData.map(row => row['Instructions per Second'] / 1e9);
    const pnkInstructions = pnkData.map(row => row['Instructions per Second'] / 1e9);
    
    const config = {
        type: 'bar',
        data: {
            labels: throughput.map(t => t.toString()),
            datasets: [
                {
                    label: 'C SIM',
                    data: csimInstructions,
                    backgroundColor: COLOR_BASELINE + 'DD',
                    borderColor: COLOR_BASELINE,
                    borderWidth: 1
                },
                {
                    label: 'PNK',
                    data: pnkInstructions,
                    backgroundColor: COLOR_COMPARATOR + 'DD',
                    borderColor: COLOR_COMPARATOR,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { font: { size: fonts.legend } }
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Requested Throughput (Mb/s)',
                        font: { size: fonts.axisLabel }
                    },
                    ticks: { font: { size: fonts.ticks } }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Instructions per Second (Billions)',
                        font: { size: fonts.axisLabel }
                    },
                    ticks: { font: { size: fonts.ticks } }
                }
            }
        }
    };
    
    if (showDiff) {
        const relativeDiff = calculateRelativeDiff(csimInstructions, pnkInstructions);
        config.data.datasets.push({
            label: 'Relative Diff (%)',
            data: relativeDiff,
            type: 'line',
            borderColor: COLOR_DIFF_LINE,
            backgroundColor: COLOR_DIFF_LINE,
            borderWidth: presentationMode ? 4 : 2,
            pointRadius: presentationMode ? 8 : 5,
            yAxisID: 'y2'
        });
        
        config.options.scales.y2 = {
            type: 'linear',
            position: 'right',
            title: {
                display: true,
                text: 'Relative Difference (%)',
                font: { size: fonts.axisLabel }
            },
            min: -20,
            max: 80,
            grid: {
                drawOnChartArea: false
            },
            ticks: { font: { size: fonts.ticks } }
        };
    }
    
    const chart = new Chart(ctx, config);
    charts.push(chart);
}

// Create CPU Utilization chart
function createCPUChart(showDiff, presentationMode) {
    const canvas = createChartContainer('System CPU Utilization vs Throughput');
    const ctx = canvas.getContext('2d');
    const fonts = getFontSizes(presentationMode);
    
    const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
    const csimCPU = csimData.map(row => row['CPU Util (Fraction)'] * 100);
    const pnkCPU = pnkData.map(row => row['CPU Util (Fraction)'] * 100);
    
    const config = {
        type: 'bar',
        data: {
            labels: throughput.map(t => t.toString()),
            datasets: [
                {
                    label: 'C SIM',
                    data: csimCPU,
                    backgroundColor: COLOR_BASELINE + 'DD',
                    borderColor: COLOR_BASELINE,
                    borderWidth: 1
                },
                {
                    label: 'PNK',
                    data: pnkCPU,
                    backgroundColor: COLOR_COMPARATOR + 'DD',
                    borderColor: COLOR_COMPARATOR,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { font: { size: fonts.legend } }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Requested Throughput (Mb/s)',
                        font: { size: fonts.axisLabel }
                    },
                    ticks: { font: { size: fonts.ticks } }
                },
                y: {
                    title: {
                        display: true,
                        text: 'CPU Utilization (%)',
                        font: { size: fonts.axisLabel }
                    },
                    max: 105,
                    ticks: { font: { size: fonts.ticks } }
                }
            }
        }
    };
    
    if (showDiff) {
        const relativeDiff = calculateRelativeDiff(csimCPU, pnkCPU);
        config.data.datasets.push({
            label: 'Relative Diff (%)',
            data: relativeDiff,
            type: 'line',
            borderColor: COLOR_DIFF_LINE,
            backgroundColor: COLOR_DIFF_LINE,
            borderWidth: presentationMode ? 4 : 2,
            pointRadius: presentationMode ? 8 : 5,
            yAxisID: 'y2'
        });
        
        config.options.scales.y2 = {
            type: 'linear',
            position: 'right',
            title: {
                display: true,
                text: 'Relative Difference (%)',
                font: { size: fonts.axisLabel }
            },
            min: -20,
            max: 80,
            grid: {
                drawOnChartArea: false
            },
            ticks: { font: { size: fonts.ticks } }
        };
    }
    
    const chart = new Chart(ctx, config);
    charts.push(chart);
}

// Create Throughput vs CPU chart
function createThroughputVsCPUChart(presentationMode) {
    const canvas = createChartContainer('Received Throughput vs Requested with CPU Utilization Overlay');
    const ctx = canvas.getContext('2d');
    const fonts = getFontSizes(presentationMode);
    
    const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
    const csimRecv = csimData.map(row => row['Recv Thrput (Mb/s)']);
    const pnkRecv = pnkData.map(row => row['Recv Thrput (Mb/s)']);
    const csimCPU = csimData.map(row => row['CPU Util (Fraction)'] * 100);
    const pnkCPU = pnkData.map(row => row['CPU Util (Fraction)'] * 100);
    
    const config = {
        type: 'bar',
        data: {
            labels: throughput.map(t => t.toString()),
            datasets: [
                {
                    label: 'C SIM Recv Throughput',
                    data: csimRecv,
                    backgroundColor: COLOR_BASELINE + 'DD',
                    borderColor: COLOR_BASELINE,
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'PNK Recv Throughput',
                    data: pnkRecv,
                    backgroundColor: COLOR_COMPARATOR + 'DD',
                    borderColor: COLOR_COMPARATOR,
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'C SIM CPU Util',
                    data: csimCPU,
                    type: 'line',
                    borderColor: COLOR_DIFF_LINE,
                    backgroundColor: 'transparent',
                    borderWidth: presentationMode ? 4 : 2,
                    pointRadius: presentationMode ? 8 : 5,
                    pointStyle: 'circle',
                    yAxisID: 'y2'
                },
                {
                    label: 'PNK CPU Util',
                    data: pnkCPU,
                    type: 'line',
                    borderColor: COLOR_DIFF_LINE,
                    backgroundColor: 'transparent',
                    borderWidth: presentationMode ? 4 : 2,
                    borderDash: [5, 5],
                    pointRadius: presentationMode ? 8 : 5,
                    pointStyle: 'rect',
                    yAxisID: 'y2'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { font: { size: fonts.legend } }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Requested Throughput (Mb/s)',
                        font: { size: fonts.axisLabel }
                    },
                    ticks: { font: { size: fonts.ticks } }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Received Throughput (Mb/s)',
                        font: { size: fonts.axisLabel }
                    },
                    ticks: { font: { size: fonts.ticks } }
                },
                y2: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'CPU Utilization (%)',
                        font: { size: fonts.axisLabel }
                    },
                    min: 0,
                    max: 105,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: { font: { size: fonts.ticks } }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, config);
    charts.push(chart);
}

// Create CPU Cycles charts
function createCyclesCharts(showDiff, presentationMode) {
    const cycleMetrics = [
        { key: 'Total Cycles', label: 'Total CPU Cycles', divisor: 1e9 },
        { key: 'Kernel Cycles', label: 'Kernel CPU Cycles', divisor: 1e9 },
        { key: 'User Cycles', label: 'User CPU Cycles', divisor: 1e9 },
        { key: 'Idle Cycles', label: 'Idle CPU Cycles', divisor: 1e9 }
    ];
    
    cycleMetrics.forEach(metric => {
        const canvas = createChartContainer(`${metric.label} vs Throughput`);
        const ctx = canvas.getContext('2d');
        const fonts = getFontSizes(presentationMode);
        
        const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
        const csimValues = csimData.map(row => row[metric.key] / metric.divisor);
        const pnkValues = pnkData.map(row => row[metric.key] / metric.divisor);
        
        const config = {
            type: 'bar',
            data: {
                labels: throughput.map(t => t.toString()),
                datasets: [
                    {
                        label: 'C SIM',
                        data: csimValues,
                        backgroundColor: COLOR_BASELINE + 'DD',
                        borderColor: COLOR_BASELINE,
                        borderWidth: 1
                    },
                    {
                        label: 'PNK',
                        data: pnkValues,
                        backgroundColor: COLOR_COMPARATOR + 'DD',
                        borderColor: COLOR_COMPARATOR,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: fonts.legend } }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Requested Throughput (Mb/s)',
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `${metric.key} (Billions)`,
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    }
                }
            }
        };
        
        if (showDiff) {
            const relativeDiff = calculateRelativeDiff(csimValues, pnkValues);
            config.data.datasets.push({
                label: 'Relative Diff (%)',
                data: relativeDiff,
                type: 'line',
                borderColor: COLOR_DIFF_LINE,
                backgroundColor: COLOR_DIFF_LINE,
                borderWidth: presentationMode ? 4 : 2,
                pointRadius: presentationMode ? 8 : 5,
                yAxisID: 'y2'
            });
            
            config.options.scales.y2 = {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: 'Relative Difference (%)',
                    font: { size: fonts.axisLabel }
                },
                min: -20,
                max: 80,
                grid: {
                    drawOnChartArea: false
                },
                ticks: { font: { size: fonts.ticks } }
            };
        }
        
        const chart = new Chart(ctx, config);
        charts.push(chart);
    });
}

// Create Cache metrics charts
function createCacheCharts(showDiff, presentationMode) {
    const cacheMetrics = [
        { key: 'L1 I-cache misses per packet', label: 'L1 I-cache Misses per Packet' },
        { key: 'L1 D-cache misses per packet', label: 'L1 D-cache Misses per Packet' },
        { key: 'L1 I-TLB misses per packet', label: 'L1 I-TLB Misses per Packet' },
        { key: 'L1 D-TLB misses per packet', label: 'L1 D-TLB Misses per Packet' },
        { key: 'instructions per packet', label: 'Instructions per Packet' },
        { key: 'Branch mis-pred per packet', label: 'Branch Mispredictions per Packet' }
    ];
    
    cacheMetrics.forEach(metric => {
        const canvas = createChartContainer(`${metric.label} vs Throughput`);
        const ctx = canvas.getContext('2d');
        const fonts = getFontSizes(presentationMode);
        
        const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
        const csimValues = csimData.map(row => row[metric.key]);
        const pnkValues = pnkData.map(row => row[metric.key]);
        
        const config = {
            type: 'bar',
            data: {
                labels: throughput.map(t => t.toString()),
                datasets: [
                    {
                        label: 'C SIM',
                        data: csimValues,
                        backgroundColor: COLOR_BASELINE + 'DD',
                        borderColor: COLOR_BASELINE,
                        borderWidth: 1
                    },
                    {
                        label: 'PNK',
                        data: pnkValues,
                        backgroundColor: COLOR_COMPARATOR + 'DD',
                        borderColor: COLOR_COMPARATOR,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: fonts.legend } }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Requested Throughput (Mb/s)',
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    },
                    y: {
                        title: {
                            display: true,
                            text: metric.label,
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    }
                }
            }
        };
        
        if (showDiff) {
            const relativeDiff = calculateRelativeDiff(csimValues, pnkValues);
            config.data.datasets.push({
                label: 'Relative Diff (%)',
                data: relativeDiff,
                type: 'line',
                borderColor: COLOR_DIFF_LINE,
                backgroundColor: COLOR_DIFF_LINE,
                borderWidth: presentationMode ? 4 : 2,
                pointRadius: presentationMode ? 8 : 5,
                yAxisID: 'y2'
            });
            
            config.options.scales.y2 = {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: 'Relative Difference (%)',
                    font: { size: fonts.axisLabel }
                },
                min: -20,
                max: 80,
                grid: {
                    drawOnChartArea: false
                },
                ticks: { font: { size: fonts.ticks } }
            };
        }
        
        const chart = new Chart(ctx, config);
        charts.push(chart);
    });
}

// Create Efficiency metrics charts
function createEfficiencyCharts(showDiff, presentationMode) {
    const efficiencyMetrics = [
        { key: 'Cycles Per Packet', label: 'Cycles per Packet', chartType: 'bar' },
        { key: 'instructions per packet', label: 'Instructions per Packet', chartType: 'bar' },
        { key: 'Branch mis-pred per packet', label: 'Branch Mispredictions per Packet', chartType: 'bar' },
        { key: 'Mean RTT (μs)', label: 'Mean Round-Trip Time (μs)', chartType: 'line' }
    ];
    
    efficiencyMetrics.forEach(metric => {
        const canvas = createChartContainer(`${metric.label} vs Throughput`);
        const ctx = canvas.getContext('2d');
        const fonts = getFontSizes(presentationMode);
        
        const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
        const csimValues = csimData.map(row => row[metric.key]);
        const pnkValues = pnkData.map(row => row[metric.key]);
        
        const datasets = [];
        
        if (metric.chartType === 'bar') {
            datasets.push(
                {
                    label: 'C SIM',
                    data: csimValues,
                    backgroundColor: COLOR_BASELINE + 'DD',
                    borderColor: COLOR_BASELINE,
                    borderWidth: 1
                },
                {
                    label: 'PNK',
                    data: pnkValues,
                    backgroundColor: COLOR_COMPARATOR + 'DD',
                    borderColor: COLOR_COMPARATOR,
                    borderWidth: 1
                }
            );
        } else {
            datasets.push(
                {
                    label: 'C SIM',
                    data: csimValues,
                    borderColor: COLOR_BASELINE,
                    backgroundColor: COLOR_BASELINE,
                    borderWidth: presentationMode ? 4 : 2,
                    pointRadius: presentationMode ? 8 : 5,
                    fill: false
                },
                {
                    label: 'PNK',
                    data: pnkValues,
                    borderColor: COLOR_COMPARATOR,
                    backgroundColor: COLOR_COMPARATOR,
                    borderWidth: presentationMode ? 4 : 2,
                    pointRadius: presentationMode ? 8 : 5,
                    pointStyle: 'rect',
                    fill: false
                }
            );
        }
        
        const config = {
            type: metric.chartType,
            data: {
                labels: throughput.map(t => t.toString()),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: fonts.legend } }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Requested Throughput (Mb/s)',
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    },
                    y: {
                        title: {
                            display: true,
                            text: metric.label,
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    }
                }
            }
        };
        
        if (showDiff) {
            const relativeDiff = calculateRelativeDiff(csimValues, pnkValues);
            config.data.datasets.push({
                label: 'Relative Diff (%)',
                data: relativeDiff,
                type: 'line',
                borderColor: COLOR_DIFF_LINE,
                backgroundColor: COLOR_DIFF_LINE,
                borderWidth: presentationMode ? 4 : 2,
                pointRadius: presentationMode ? 8 : 5,
                yAxisID: 'y2'
            });
            
            config.options.scales.y2 = {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: 'Relative Difference (%)',
                    font: { size: fonts.axisLabel }
                },
                min: -20,
                max: 80,
                grid: {
                    drawOnChartArea: false
                },
                ticks: { font: { size: fonts.ticks } }
            };
        }
        
        const chart = new Chart(ctx, config);
        charts.push(chart);
    });
}

// Create Packet metrics charts
function createPacketCharts(showDiff, presentationMode) {
    const packetMetrics = [
        { key: 'Packet Rate (p/s)', label: 'Packet Rate (Kpps)', divisor: 1000 },
        { key: 'Recv Thrput (Mb/s)', label: 'Received Throughput (Mb/s)', divisor: 1 },
        { key: 'Send Thrput (Mb/s)', label: 'Sent Throughput (Mb/s)', divisor: 1 }
    ];
    
    packetMetrics.forEach(metric => {
        const canvas = createChartContainer(`${metric.label} vs Throughput`);
        const ctx = canvas.getContext('2d');
        const fonts = getFontSizes(presentationMode);
        
        const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
        const csimValues = csimData.map(row => row[metric.key] / metric.divisor);
        const pnkValues = pnkData.map(row => row[metric.key] / metric.divisor);
        
        const config = {
            type: 'bar',
            data: {
                labels: throughput.map(t => t.toString()),
                datasets: [
                    {
                        label: 'C SIM',
                        data: csimValues,
                        backgroundColor: COLOR_BASELINE + 'DD',
                        borderColor: COLOR_BASELINE,
                        borderWidth: 1
                    },
                    {
                        label: 'PNK',
                        data: pnkValues,
                        backgroundColor: COLOR_COMPARATOR + 'DD',
                        borderColor: COLOR_COMPARATOR,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: { font: { size: fonts.legend } }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Requested Throughput (Mb/s)',
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    },
                    y: {
                        title: {
                            display: true,
                            text: metric.label,
                            font: { size: fonts.axisLabel }
                        },
                        ticks: { font: { size: fonts.ticks } }
                    }
                }
            }
        };
        
        if (showDiff) {
            const relativeDiff = calculateRelativeDiff(csimValues, pnkValues);
            config.data.datasets.push({
                label: 'Relative Diff (%)',
                data: relativeDiff,
                type: 'line',
                borderColor: COLOR_DIFF_LINE,
                backgroundColor: COLOR_DIFF_LINE,
                borderWidth: presentationMode ? 4 : 2,
                pointRadius: presentationMode ? 8 : 5,
                yAxisID: 'y2'
            });
            
            config.options.scales.y2 = {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: 'Relative Difference (%)',
                    font: { size: fonts.axisLabel }
                },
                min: -20,
                max: 80,
                grid: {
                    drawOnChartArea: false
                },
                ticks: { font: { size: fonts.ticks } }
            };
        }
        
        const chart = new Chart(ctx, config);
        charts.push(chart);
    });
}

// Create Component CPU utilization charts
function createComponentCharts(showDiff, presentationMode) {
    const components = [
        { key: 'ethernet_driver_CPU_Util', label: 'Ethernet Driver CPU Utilization' },
        { key: 'net_virt_tx_CPU_Util', label: 'Net Virt TX CPU Utilization' },
        { key: 'net_virt_rx_CPU_Util', label: 'Net Virt RX CPU Utilization' },
        { key: 'client0_CPU_Util', label: 'Client0 CPU Utilization' },
        { key: 'client0_net_copier_CPU_Util', label: 'Client0 Net Copier CPU Utilization' }
    ];
    
    components.forEach(component => {
        if (csimData[0][component.key] !== undefined) {
            const canvas = createChartContainer(`${component.label} vs Throughput`);
            const ctx = canvas.getContext('2d');
            const fonts = getFontSizes(presentationMode);
            
            const throughput = csimData.map(row => row['Requ Thrput (Mb/s)']);
            const csimValues = csimData.map(row => row[component.key]);
            const pnkValues = pnkData.map(row => row[component.key]);
            
            const config = {
                type: 'bar',
                data: {
                    labels: throughput.map(t => t.toString()),
                    datasets: [
                        {
                            label: 'C SIM',
                            data: csimValues,
                            backgroundColor: COLOR_BASELINE + 'DD',
                            borderColor: COLOR_BASELINE,
                            borderWidth: 1
                        },
                        {
                            label: 'PNK',
                            data: pnkValues,
                            backgroundColor: COLOR_COMPARATOR + 'DD',
                            borderColor: COLOR_COMPARATOR,
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: { font: { size: fonts.legend } }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Requested Throughput (Mb/s)',
                                font: { size: fonts.axisLabel }
                            },
                            ticks: { font: { size: fonts.ticks } }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'CPU Utilization (%)',
                                font: { size: fonts.axisLabel }
                            },
                            ticks: { font: { size: fonts.ticks } }
                        }
                    }
                }
            };
            
            if (showDiff) {
                const relativeDiff = calculateRelativeDiff(csimValues, pnkValues);
                config.data.datasets.push({
                    label: 'Relative Diff (%)',
                    data: relativeDiff,
                    type: 'line',
                    borderColor: COLOR_DIFF_LINE,
                    backgroundColor: COLOR_DIFF_LINE,
                    borderWidth: presentationMode ? 4 : 2,
                    pointRadius: presentationMode ? 8 : 5,
                    yAxisID: 'y2'
                });
                
                config.options.scales.y2 = {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Relative Difference (%)',
                        font: { size: fonts.axisLabel }
                    },
                    min: -20,
                    max: 80,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: { font: { size: fonts.ticks } }
                };
            }
            
            const chart = new Chart(ctx, config);
            charts.push(chart);
        }
    });
}

// Event listeners
document.getElementById('metricSelect').addEventListener('change', updateVisualizations);
document.getElementById('diffToggle').addEventListener('change', updateVisualizations);
document.getElementById('presentationMode').addEventListener('change', updateVisualizations);

// Initial load
window.addEventListener('load', loadData);