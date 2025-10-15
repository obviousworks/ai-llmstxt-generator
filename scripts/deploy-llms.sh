#!/bin/bash
# LLMs.txt Generator - Deployment Script
# Deploys generated llms.txt files to target websites

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/../config/websites.conf}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

# Initialize log
echo "=========================================" | tee -a "$LOG_FILE"
echo "$(date): Starting llms.txt deployment" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"

# Statistics
TOTAL_DEPLOYMENTS=${#DEPLOY_TARGETS[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
declare -a FAILED_DEPLOYMENTS

# Function to deploy files for a domain
deploy_for_domain() {
    local domain="$1"
    local target="$2"
    local source_llms="$OUTPUT_DIR/${domain}_llms.txt"
    local source_full="$OUTPUT_DIR/${domain}_llms-full.txt"
    
    echo "" | tee -a "$LOG_FILE"
    echo "📦 Deploying: $domain" | tee -a "$LOG_FILE"
    echo "   Target: $target" | tee -a "$LOG_FILE"
    
    # Check if source files exist
    if [ ! -f "$source_llms" ]; then
        echo "⚠️  Source file not found: $source_llms" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Determine deployment method (local or remote)
    if [[ "$target" == *"@"* ]]; then
        # Remote deployment via SCP
        echo "   Method: Remote (SCP)" | tee -a "$LOG_FILE"
        
        if scp "$source_llms" "$target/llms.txt" 2>&1 | tee -a "$LOG_FILE"; then
            if scp "$source_full" "$target/llms-full.txt" 2>&1 | tee -a "$LOG_FILE"; then
                echo "$(date): ✅ Remote deployment successful: $domain" >> "$LOG_FILE"
                return 0
            fi
        fi
        
        echo "$(date): ❌ Remote deployment failed: $domain" | tee -a "$LOG_FILE"
        return 1
    else
        # Local deployment
        echo "   Method: Local (copy)" | tee -a "$LOG_FILE"
        
        # Create target directory if it doesn't exist
        mkdir -p "$target" 2>&1 | tee -a "$LOG_FILE"
        
        if cp "$source_llms" "$target/llms.txt" 2>&1 | tee -a "$LOG_FILE"; then
            if cp "$source_full" "$target/llms-full.txt" 2>&1 | tee -a "$LOG_FILE"; then
                # Set proper permissions
                chmod 644 "$target/llms.txt" "$target/llms-full.txt" 2>&1 | tee -a "$LOG_FILE"
                echo "$(date): ✅ Local deployment successful: $domain" >> "$LOG_FILE"
                return 0
            fi
        fi
        
        echo "$(date): ❌ Local deployment failed: $domain" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Deploy to each target
for domain in "${!DEPLOY_TARGETS[@]}"; do
    target="${DEPLOY_TARGETS[$domain]}"
    
    if deploy_for_domain "$domain" "$target"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_DEPLOYMENTS+=("$domain")
    fi
done

# Summary
echo "" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "📊 Deployment Summary" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "Total Deployments: $TOTAL_DEPLOYMENTS" | tee -a "$LOG_FILE"
echo "✅ Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "❌ Failed: $FAILED_COUNT" | tee -a "$LOG_FILE"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "Failed deployments:" | tee -a "$LOG_FILE"
    for domain in "${FAILED_DEPLOYMENTS[@]}"; do
        echo "  - $domain" | tee -a "$LOG_FILE"
    done
fi

echo "" | tee -a "$LOG_FILE"
echo "$(date): Deployment completed" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"

# Send notifications if enabled
if [ "$ENABLE_EMAIL_NOTIFICATIONS" = true ] && [ ! -z "$NOTIFICATION_EMAIL" ]; then
    echo "Sending email notification to $NOTIFICATION_EMAIL..."
    echo "LLMs.txt Deployment Complete: $SUCCESS_COUNT/$TOTAL_DEPLOYMENTS successful" | \
        mail -s "LLMs.txt Deployment Report" "$NOTIFICATION_EMAIL"
fi

if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"LLMs.txt Deployment Complete: $SUCCESS_COUNT/$TOTAL_DEPLOYMENTS successful\"}" \
        --silent > /dev/null
fi

# Exit with error if any deployment failed
if [ $FAILED_COUNT -gt 0 ]; then
    exit 1
fi

exit 0
