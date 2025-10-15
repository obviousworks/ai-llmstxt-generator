#!/bin/bash
# LLMs.txt Generator - Cron Setup Script
# Sets up automated bi-weekly generation

set -e

echo "=========================================="
echo "LLMs.txt Generator - Cron Setup"
echo "=========================================="

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/../config/websites.conf}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

echo ""
echo "📋 Configuration:"
echo "   Schedule: $CRON_SCHEDULE"
echo "   Generate Script: $SCRIPT_DIR/generate-llms.sh"
echo "   Deploy Script: $SCRIPT_DIR/deploy-llms.sh"
echo "   Log File: $LOG_FILE"
echo ""

# Explain schedule
echo "📅 Schedule Explanation:"
case "$CRON_SCHEDULE" in
    "0 2 */14 * *")
        echo "   Every 2 weeks at 2:00 AM"
        ;;
    "0 2 * * 1")
        echo "   Every Monday at 2:00 AM"
        ;;
    "0 2 1 * *")
        echo "   First day of every month at 2:00 AM"
        ;;
    *)
        echo "   Custom schedule: $CRON_SCHEDULE"
        ;;
esac

echo ""
read -p "Continue with cron installation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Create log directory
LOG_DIR=$(dirname "$LOG_FILE")
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 Creating log directory: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown $USER:$USER "$LOG_DIR"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$SCRIPT_DIR/generate-llms.sh"
chmod +x "$SCRIPT_DIR/deploy-llms.sh"

# Create combined cron command
CRON_COMMAND="$CRON_SCHEDULE $SCRIPT_DIR/generate-llms.sh && $SCRIPT_DIR/deploy-llms.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "generate-llms.sh"; then
    echo ""
    echo "⚠️  Existing cron job found!"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "generate-llms.sh" || true
    echo ""
    read -p "Remove existing and install new? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Remove existing cron job
    crontab -l | grep -v "generate-llms.sh" | crontab -
    echo "✅ Removed existing cron job"
fi

# Install new cron job
echo "📦 Installing cron job..."
(crontab -l 2>/dev/null || true; echo "$CRON_COMMAND") | crontab -

echo ""
echo "=========================================="
echo "✅ Cron Job Installed Successfully!"
echo "=========================================="
echo ""
echo "📋 Installed cron job:"
crontab -l | grep "generate-llms.sh"
echo ""
echo "🔧 Useful commands:"
echo "   View cron jobs:    crontab -l"
echo "   Edit cron jobs:    crontab -e"
echo "   Remove cron jobs:  crontab -r"
echo "   View logs:         tail -f $LOG_FILE"
echo ""
echo "🧪 Test the scripts manually:"
echo "   $SCRIPT_DIR/generate-llms.sh"
echo "   $SCRIPT_DIR/deploy-llms.sh"
echo ""
echo "📅 Next scheduled run:"
# Calculate next run time (approximate)
if command -v python3 &> /dev/null; then
    python3 << EOF
from datetime import datetime, timedelta
import re

schedule = "$CRON_SCHEDULE"
parts = schedule.split()
minute, hour = parts[0], parts[1]

now = datetime.now()
if minute == "0" and hour == "2":
    # Find next 2 AM
    next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)
    
    # Check if it's a bi-weekly schedule
    if "*/14" in schedule:
        print(f"   Approximately: {next_run.strftime('%Y-%m-%d %H:%M')} (or 14 days later)")
    else:
        print(f"   {next_run.strftime('%Y-%m-%d %H:%M')}")
else:
    print("   Check with: crontab -l")
EOF
else
    echo "   Check with: crontab -l"
fi

echo ""
echo "🎯 Next steps:"
echo "   1. Edit config/websites.conf to add your websites"
echo "   2. Test generation: ./scripts/generate-llms.sh"
echo "   3. Test deployment: ./scripts/deploy-llms.sh"
echo "   4. Monitor logs: tail -f $LOG_FILE"
echo ""
