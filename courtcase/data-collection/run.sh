#!/bin/bash
#
# IndianKanoon Production Scraper - Run Script
# Quick starter script for common operations
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Print banner
echo -e "${BLUE}"
echo "============================================================================"
echo "IndianKanoon Production Scraper"
echo "============================================================================"
echo -e "${NC}"

# Parse command
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  collect          - Collect all document URLs"
    echo "  collect-test     - Collect URLs (test with 10 pages)"
    echo "  scrape           - Download and upload PDFs"
    echo "  scrape-test      - Download PDFs (test with 100 docs)"
    echo "  status           - Show current progress"
    echo "  resume           - Resume interrupted downloads"
    echo "  authenticate     - Authenticate Google Drive"
    echo ""
    echo "Examples:"
    echo "  ./run.sh collect-test"
    echo "  ./run.sh scrape"
    echo "  ./run.sh status"
    exit 0
fi

COMMAND=$1

case $COMMAND in
    collect)
        echo -e "${GREEN}Starting URL collection...${NC}"
        python main_scraper.py --mode collect
        ;;

    collect-test)
        echo -e "${YELLOW}Starting URL collection (TEST MODE - 10 pages)...${NC}"
        python main_scraper.py --mode collect --max-pages 10
        ;;

    scrape)
        echo -e "${GREEN}Starting PDF download and upload...${NC}"
        python main_scraper.py --mode scrape
        ;;

    scrape-test)
        echo -e "${YELLOW}Starting PDF download (TEST MODE - 100 docs)...${NC}"
        python main_scraper.py --mode scrape --batch-size 100
        ;;

    scrape-batch)
        BATCH_SIZE=${2:-1000}
        echo -e "${GREEN}Starting PDF download (batch size: $BATCH_SIZE)...${NC}"
        python main_scraper.py --mode scrape --batch-size $BATCH_SIZE
        ;;

    status)
        echo -e "${BLUE}Checking status...${NC}"
        python main_scraper.py --mode status
        ;;

    resume)
        echo -e "${GREEN}Resuming downloads...${NC}"
        python main_scraper.py --mode resume
        ;;

    authenticate)
        echo -e "${BLUE}Authenticating Google Drive...${NC}"
        python - << EOF
from scraper.drive_manager import DriveManager
import yaml

# Load config
with open('./config/config_production.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Authenticate
dm = DriveManager(config)
if dm.authenticate():
    print("✓ Authentication successful!")
    print(f"✓ Token saved to {dm.token_file}")
else:
    print("✗ Authentication failed")
EOF
        ;;

    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run './run.sh' without arguments to see usage."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done.${NC}"
