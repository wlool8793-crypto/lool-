#!/bin/bash
#
# IndianKanoon Production Scraper - Setup Script for GCP VM
# This script installs all dependencies on a fresh Ubuntu VM
#

set -e  # Exit on error

echo "============================================================================"
echo "IndianKanoon Production Scraper - Setup Script"
echo "============================================================================"

# Update system
echo ""
echo "📦 Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Install Python and pip
echo ""
echo "🐍 Installing Python 3..."
sudo apt-get install -y -qq python3 python3-pip python3-venv

# Install Chrome
echo ""
echo "🌐 Installing Google Chrome..."
cd /tmp
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y -qq ./google-chrome-stable_current_amd64.deb

# Verify Chrome installation
google-chrome --version

# Install ChromeDriver
echo ""
echo "🚗 Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify ChromeDriver installation
chromedriver --version

# Clean up
rm -f google-chrome-stable_current_amd64.deb chromedriver_linux64.zip

# Install system dependencies
echo ""
echo "📚 Installing system dependencies..."
sudo apt-get install -y -qq \
    git \
    curl \
    wget \
    unzip \
    tmux \
    htop \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Create project directory
echo ""
echo "📁 Setting up project directory..."
cd ~
if [ -d "indiankanoon-scraper" ]; then
    echo "Project directory already exists"
else
    mkdir -p indiankanoon-scraper
fi

cd indiankanoon-scraper

# Create directory structure
mkdir -p data/temp_pdfs
mkdir -p logs
mkdir -p config

# Create virtual environment
echo ""
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip -q

# Install Python dependencies
echo ""
echo "📥 Installing Python packages..."
if [ -f "requirements_production.txt" ]; then
    pip install -r requirements_production.txt -q
else
    echo "⚠️  requirements_production.txt not found. You'll need to install dependencies manually."
fi

# Create .env template
echo ""
echo "📝 Creating .env template..."
cat > .env << EOF
# IndianKanoon Production Scraper Environment Variables
DATABASE_URL=sqlite:///data/indiankanoon_production.db
LOG_LEVEL=INFO
HEADLESS_MODE=true

# Google Drive (optional - will use credentials.json)
# GOOGLE_APPLICATION_CREDENTIALS=./config/credentials.json
EOF

# Create .gitignore
echo ""
echo "📝 Creating .gitignore..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data files
*.db
*.db-journal
data/
logs/
*.log

# Credentials
config/credentials.json
config/token.pickle
.env

# Temporary files
*.tmp
*.swp
*~

# IDE
.vscode/
.idea/
*.sublime-*

# OS
.DS_Store
Thumbs.db

# PDFs
*.pdf

# Checkpoints
*.json
!config/credentials.template.json
EOF

# Print Chrome and ChromeDriver info
echo ""
echo "============================================================================"
echo "✓ Setup Complete!"
echo "============================================================================"
echo ""
echo "Installed versions:"
google-chrome --version
chromedriver --version
python3 --version
echo ""
echo "Next steps:"
echo "1. Upload credentials.json to ./config/"
echo "2. Review and adjust config/config_production.yaml"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run URL collection: python main_scraper.py --mode collect --max-pages 10"
echo "5. Run scraper: python main_scraper.py --mode scrape --batch-size 100"
echo ""
echo "For production run:"
echo "  tmux new -s scraper"
echo "  python main_scraper.py --mode collect"
echo "  python main_scraper.py --mode scrape"
echo ""
echo "To monitor: tmux attach -t scraper"
echo "To detach: Ctrl+B, then D"
echo ""
echo "============================================================================"
