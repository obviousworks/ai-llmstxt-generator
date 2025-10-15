#!/bin/bash
# LLMs.txt Generator - Automated Generation Script
# Generates llms.txt files for configured websites

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/../config/websites.conf}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Initialize log file
echo "=========================================" | tee -a "$LOG_FILE"
echo "$(date): Starting bi-weekly llms.txt generation" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"

# Statistics
TOTAL_SITES=${#WEBSITES[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
declare -a FAILED_SITES

# Function to generate llms.txt for a website
generate_for_website() {
    local website="$1"
    local domain=$(echo "$website" | sed 's|https\?://||' | sed 's|/.*||')
    local max_pages=${GENERATION_SETTINGS[$domain]:-20}
    local retry_count=0
    
    echo "" | tee -a "$LOG_FILE"
    echo "📝 Processing: $website" | tee -a "$LOG_FILE"
    echo "   Domain: $domain" | tee -a "$LOG_FILE"
    echo "   Max Pages: $max_pages" | tee -a "$LOG_FILE"
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        # Generate llms.txt via API
        response=$(curl -X POST "$API_URL/generate" \
            -H "Content-Type: application/json" \
            -d "{\"url\": \"$website\", \"max_pages\": $max_pages}" \
            --silent --show-error --max-time 300 2>&1)
        
        if [ $? -eq 0 ]; then
            # Extract and save files
            echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    with open('$OUTPUT_DIR/${domain}_llms.txt', 'w') as f:
        f.write(data['llms_txt'])
    with open('$OUTPUT_DIR/${domain}_llms-full.txt', 'w') as f:
        f.write(data['llms_full_txt'])
    print('✅ Successfully generated files for $domain')
    sys.exit(0)
except Exception as e:
    print(f'❌ Error processing response: {e}')
    sys.exit(1)
            " 2>&1 | tee -a "$LOG_FILE"
            
            if [ ${PIPESTATUS[1]} -eq 0 ]; then
                echo "$(date): ✅ Success: $domain" >> "$LOG_FILE"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            echo "⚠️  Retry $retry_count/$MAX_RETRIES for $domain..." | tee -a "$LOG_FILE"
            sleep $RETRY_DELAY
        fi
    done
    
    echo "$(date): ❌ Failed after $MAX_RETRIES attempts: $domain" | tee -a "$LOG_FILE"
    return 1
}

# Process each website
for website in "${WEBSITES[@]}"; do
    if generate_for_website "$website"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_SITES+=("$website")
    fi
    
    # Rate limiting
    if [ ${#WEBSITES[@]} -gt 1 ]; then
        sleep $RATE_LIMIT_DELAY
    fi
done

# Cleanup old files if enabled
if [ "$CLEANUP_OLD_FILES" = true ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "🧹 Cleaning up files older than $CLEANUP_DAYS days..." | tee -a "$LOG_FILE"
    find "$OUTPUT_DIR" -name "*.txt" -mtime +$CLEANUP_DAYS -delete 2>&1 | tee -a "$LOG_FILE"
fi

# Summary
echo "" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "📊 Generation Summary" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "Total Sites: $TOTAL_SITES" | tee -a "$LOG_FILE"
echo "✅ Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "❌ Failed: $FAILED_COUNT" | tee -a "$LOG_FILE"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "Failed sites:" | tee -a "$LOG_FILE"
    for site in "${FAILED_SITES[@]}"; do
        echo "  - $site" | tee -a "$LOG_FILE"
    done
fi

echo "" | tee -a "$LOG_FILE"
echo "$(date): Generation completed" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"

# Send notifications if enabled
if [ "$ENABLE_EMAIL_NOTIFICATIONS" = true ] && [ ! -z "$NOTIFICATION_EMAIL" ]; then
    echo "Sending email notification to $NOTIFICATION_EMAIL..."
    echo "LLMs.txt Generation Complete: $SUCCESS_COUNT/$TOTAL_SITES successful" | \
        mail -s "LLMs.txt Generation Report" "$NOTIFICATION_EMAIL"
fi

if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"LLMs.txt Generation Complete: $SUCCESS_COUNT/$TOTAL_SITES successful\"}" \
        --silent > /dev/null
fi

# Exit with error if any generation failed
if [ $FAILED_COUNT -gt 0 ]; then
    exit 1
fi

exit 0
