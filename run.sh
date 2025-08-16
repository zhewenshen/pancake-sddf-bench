#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_usage() {
    echo "Usage: $0 <iq_file1> <processed_file1> <iq_file2> <processed_file2> [output_dir] [dataset1_name] [dataset2_name]"
    echo ""
    echo "Arguments:"
    echo "  iq_file1        First dataset IQ file (performance data)"
    echo "  processed_file1 First dataset processed file (utilization data)"
    echo "  iq_file2        Second dataset IQ file (performance data)"
    echo "  processed_file2 Second dataset processed file (utilization data)"
    echo "  output_dir      Output directory (default: output)"
    echo "  dataset1_name   First dataset label (default: extracted from filename)"
    echo "  dataset2_name   Second dataset label (default: extracted from filename)"
    echo ""
    echo "Examples:"
    echo "  $0 config1_iq.txt config1_processed.txt config2_iq.txt config2_processed.txt results"
    echo ""
    echo "  $0 c_overflow_iq_data.txt c_overflow_processed_data.txt c_overflow_iq_data.txt c_overflow_processed_data.txt results"
    echo ""
    echo "  $0 test1_iq.txt test1_proc.txt test2_iq.txt test2_proc.txt results \"Baseline\" \"Optimized\""
    echo ""
    echo "This will generate:"
    echo "  output/dataset1_data.csv         - First dataset structured data"
    echo "  output/dataset2_data.csv         - Second dataset structured data" 
    echo "  output/comparison_analysis.pdf   - Comprehensive comparison analysis"
}

if [ $# -lt 4 ]; then
    log_error "Missing required arguments"
    echo ""
    show_usage
    exit 1
fi

IQ_FILE1="$1"
PROCESSED_FILE1="$2"
IQ_FILE2="$3"
PROCESSED_FILE2="$4"
OUTPUT_DIR="${5:-output}"

if [ -n "$6" ]; then
    DATASET1_NAME="$6"
else
    BASENAME=$(basename "$IQ_FILE1")
    DATASET1_NAME=$(echo "$BASENAME" | sed 's/_iq_data\.txt$//' | sed 's/_iq\.txt$//' | sed 's/\.txt$//')
    log_info "Using dataset1 name extracted from filename: $DATASET1_NAME"
fi

if [ -n "$7" ]; then
    DATASET2_NAME="$7"
else
    BASENAME=$(basename "$IQ_FILE2")
    DATASET2_NAME=$(echo "$BASENAME" | sed 's/_iq_data\.txt$//' | sed 's/_iq\.txt$//' | sed 's/\.txt$//')
    log_info "Using dataset2 name extracted from filename: $DATASET2_NAME"
fi

if [ ! -f "$IQ_FILE1" ]; then
    log_error "First IQ file not found: $IQ_FILE1"
    exit 1
fi

if [ ! -f "$PROCESSED_FILE1" ]; then
    log_error "First processed file not found: $PROCESSED_FILE1"
    exit 1
fi

if [ ! -f "$IQ_FILE2" ]; then
    log_error "Second IQ file not found: $IQ_FILE2"
    exit 1
fi

if [ ! -f "$PROCESSED_FILE2" ]; then
    log_error "Second processed file not found: $PROCESSED_FILE2"
    exit 1
fi

if [ ! -f "parse.py" ]; then
    log_error "parse.py not found in current directory"
    exit 1
fi

if [ ! -f "plot.py" ]; then
    log_error "plot.py not found in current directory"
    exit 1
fi

log_info "Creating output directory: $OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

CSV_FILE1="$OUTPUT_DIR/${DATASET1_NAME}_data.csv"
CSV_FILE2="$OUTPUT_DIR/${DATASET2_NAME}_data.csv"
PDF_FILE="$OUTPUT_DIR/comparison_analysis.pdf"

log_info "Parsing first dataset..."
log_info "  IQ file: $IQ_FILE1"
log_info "  Processed file: $PROCESSED_FILE1"
log_info "  Output CSV: $CSV_FILE1"

if python parse.py "$IQ_FILE1" "$PROCESSED_FILE1" "$CSV_FILE1"; then
    log_success "First dataset parsing completed successfully"
else
    log_error "First dataset parsing failed"
    exit 1
fi

if [ ! -f "$CSV_FILE1" ]; then
    log_error "First CSV file was not created: $CSV_FILE1"
    exit 1
fi

CSV1_LINES=$(wc -l < "$CSV_FILE1")
DATA1_RECORDS=$((CSV1_LINES - 1))
log_info "Generated first CSV with $DATA1_RECORDS data records"

log_info "Parsing second dataset..."
log_info "  IQ file: $IQ_FILE2"
log_info "  Processed file: $PROCESSED_FILE2"
log_info "  Output CSV: $CSV_FILE2"

if python parse.py "$IQ_FILE2" "$PROCESSED_FILE2" "$CSV_FILE2"; then
    log_success "Second dataset parsing completed successfully"
else
    log_error "Second dataset parsing failed"
    exit 1
fi

if [ ! -f "$CSV_FILE2" ]; then
    log_error "Second CSV file was not created: $CSV_FILE2"
    exit 1
fi

CSV2_LINES=$(wc -l < "$CSV_FILE2")
DATA2_RECORDS=$((CSV2_LINES - 1))
log_info "Generated second CSV with $DATA2_RECORDS data records"

log_info "Generating comparative analysis..."
log_info "  First dataset CSV: $CSV_FILE1" 
log_info "  Second dataset CSV: $CSV_FILE2"
log_info "  Output PDF: $PDF_FILE"
log_info "  Dataset labels: '$DATASET1_NAME' vs '$DATASET2_NAME'"

if python plot.py "$CSV_FILE1" "$CSV_FILE2" "$PDF_FILE" "$DATASET1_NAME" "$DATASET2_NAME"; then
    log_success "Comparison analysis generation completed successfully"
else
    log_error "Comparison analysis generation failed"
    exit 1
fi

if [ ! -f "$PDF_FILE" ]; then
    log_error "PDF file was not created: $PDF_FILE"
    exit 1
fi

PDF_SIZE=$(du -h "$PDF_FILE" | cut -f1)

echo ""
log_success "Analysis pipeline completed successfully!"
echo ""
echo "Generated files:"
echo "  📊 Dataset 1: $CSV_FILE1 ($DATA1_RECORDS records)"
echo "  📊 Dataset 2: $CSV_FILE2 ($DATA2_RECORDS records)"
echo "  📈 Comparison: $PDF_FILE ($PDF_SIZE)"
echo ""
echo "The comparison analysis includes:"
echo "  • $DATA1_RECORDS vs $DATA2_RECORDS test iterations compared"
echo "  • Full component CPU utilization tracking for both datasets"
echo "  • Instructions per second comparative analysis"
echo "  • Comprehensive performance metrics comparison"
echo "  • Professional visualization with standard comparison format"
echo ""
log_info "Comparison analysis ready for review!"