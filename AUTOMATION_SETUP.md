# ⏰ Automation Setup Guide

Complete guide for automated bi-weekly llms.txt generation and deployment.

## 🚀 Quick Start (3 Steps)

### 1. Configure Websites

```bash
# Edit configuration file
nano config/websites.conf

# Add your websites and deployment targets
WEBSITES=(
    "https://your-website.com"
    "https://another-site.com"
)

DEPLOY_TARGETS=(
    ["your-website.com"]="/var/www/your-site/public"
    ["another-site.com"]="user@server:/var/www/html"
)
```

### 2. Test Scripts

```bash
# Test generation
./scripts/generate-llms.sh

# Test deployment
./scripts/deploy-llms.sh

# Check output
ls -la /var/www/generated-llms/
```

### 3. Setup Cron Job

```bash
# Install automated bi-weekly execution
./scripts/setup-cron.sh

# Verify installation
crontab -l
```

**Done!** Files will be generated and deployed every 2 weeks automatically.

---

## 📋 Configuration

### Website Configuration

Edit `config/websites.conf`:

```bash
# Websites to generate llms.txt for
WEBSITES=(
    "https://obviousworks.ch"
    "https://your-website.com"
)

# Custom generation settings per domain
declare -A GENERATION_SETTINGS=(
    ["obviousworks.ch"]="50"      # Generate from 50 pages
    ["your-website.com"]="20"     # Generate from 20 pages
)

# Deployment targets
declare -A DEPLOY_TARGETS=(
    # Local deployment
    ["obviousworks.ch"]="/var/www/obviousworks/public"
    
    # Remote deployment via SCP
    ["your-website.com"]="user@server.com:/var/www/html"
)
```

### Schedule Configuration

Default: Every 2 weeks on Monday at 2 AM

```bash
CRON_SCHEDULE="0 2 */14 * *"
```

**Alternative schedules:**

```bash
# Weekly (every Monday at 2 AM)
CRON_SCHEDULE="0 2 * * 1"

# Monthly (first day of month at 2 AM)
CRON_SCHEDULE="0 2 1 * *"

# Every 3 weeks
CRON_SCHEDULE="0 2 */21 * *"

# Custom (every Friday at 3 AM)
CRON_SCHEDULE="0 3 * * 5"
```

---

## 🔧 Scripts Overview

### generate-llms.sh

Generates llms.txt files for all configured websites.

**Features:**
- ✅ Automatic retry on failure (3 attempts)
- ✅ Rate limiting between requests
- ✅ Detailed logging
- ✅ Statistics and summary
- ✅ Email/Slack notifications (optional)
- ✅ Cleanup of old files

**Usage:**
```bash
# Basic usage
./scripts/generate-llms.sh

# With custom config
CONFIG_FILE=/path/to/custom.conf ./scripts/generate-llms.sh

# View logs
tail -f /var/log/llms-generator.log
```

### deploy-llms.sh

Deploys generated files to target websites.

**Features:**
- ✅ Local and remote deployment (SCP)
- ✅ Automatic directory creation
- ✅ Permission management
- ✅ Deployment verification
- ✅ Rollback on failure

**Usage:**
```bash
# Basic usage
./scripts/deploy-llms.sh

# Deploy specific domain
# (edit script to add domain filter)

# Test deployment (dry-run)
# Add DRY_RUN=true to config
```

### setup-cron.sh

Installs cron job for automated execution.

**Features:**
- ✅ Interactive installation
- ✅ Existing job detection
- ✅ Schedule validation
- ✅ Next run calculation

**Usage:**
```bash
# Install cron job
./scripts/setup-cron.sh

# View installed jobs
crontab -l

# Remove cron job
crontab -e  # Delete the line manually
```

### health-check.sh

Monitors services and restarts if needed.

**Features:**
- ✅ Backend API health check
- ✅ Frontend health check
- ✅ Automatic restart (systemd or Docker)
- ✅ Health logging

**Usage:**
```bash
# Manual health check
./scripts/health-check.sh

# Add to cron for monitoring (every 5 minutes)
*/5 * * * * /path/to/scripts/health-check.sh
```

---

## 📊 Monitoring & Logs

### View Logs

```bash
# Real-time log monitoring
tail -f /var/log/llms-generator.log

# Last 100 lines
tail -n 100 /var/log/llms-generator.log

# Search for errors
grep "❌" /var/log/llms-generator.log

# Search for successful generations
grep "✅" /var/log/llms-generator.log

# View logs from today
grep "$(date +%Y-%m-%d)" /var/log/llms-generator.log
```

### Log Rotation

Setup log rotation to prevent large log files:

```bash
sudo nano /etc/logrotate.d/llms-generator
```

Add:
```
/var/log/llms-generator.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}
```

### Statistics

Check generation statistics:

```bash
# Count successful generations
grep "✅ Success" /var/log/llms-generator.log | wc -l

# Count failures
grep "❌ Failed" /var/log/llms-generator.log | wc -l

# Last generation summary
grep "Generation Summary" -A 5 /var/log/llms-generator.log | tail -6
```

---

## 🔔 Notifications

### Email Notifications

Enable in `config/websites.conf`:

```bash
ENABLE_EMAIL_NOTIFICATIONS=true
NOTIFICATION_EMAIL="admin@example.com"
```

**Requirements:**
```bash
# Install mailutils
sudo apt install mailutils

# Test email
echo "Test" | mail -s "Test" admin@example.com
```

### Slack Notifications

Add webhook URL in `config/websites.conf`:

```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Get webhook URL:**
1. Go to https://api.slack.com/apps
2. Create new app → Incoming Webhooks
3. Activate and add to workspace
4. Copy webhook URL

---

## 🐛 Troubleshooting

### Generation Fails

```bash
# Check API is running
curl http://localhost:8000/health

# Test generation manually
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "max_pages": 5}'

# Check OpenAI API key
grep OPENAI_API_KEY /etc/systemd/system/llms-api.service
```

### Deployment Fails

```bash
# Check permissions
ls -la /var/www/generated-llms/

# Test local deployment
cp /var/www/generated-llms/example.com_llms.txt /tmp/test.txt

# Test remote deployment
scp /var/www/generated-llms/example.com_llms.txt user@server:/tmp/
```

### Cron Not Running

```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog

# Verify cron job
crontab -l

# Test cron job manually
/path/to/scripts/generate-llms.sh && /path/to/scripts/deploy-llms.sh
```

### Permission Issues

```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix log directory permissions
sudo chown -R $USER:$USER /var/log/llms-generator

# Fix output directory permissions
sudo chown -R $USER:$USER /var/www/generated-llms
```

---

## 🔒 Security Best Practices

### SSH Keys for Remote Deployment

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "llms-generator"

# Copy to remote server
ssh-copy-id user@server.com

# Test connection
ssh user@server.com "echo 'Connection successful'"
```

### Restrict Script Permissions

```bash
# Only owner can execute
chmod 700 scripts/*.sh

# Protect configuration
chmod 600 config/websites.conf
```

### Secure API Key

```bash
# Use environment file instead of hardcoding
echo "OPENAI_API_KEY=your_key" > /opt/llms-generator/.env
chmod 600 /opt/llms-generator/.env

# Reference in systemd service
EnvironmentFile=/opt/llms-generator/.env
```

---

## 📈 Advanced Configuration

### Multiple Environments

```bash
# Production config
CONFIG_FILE=/etc/llms-generator/production.conf ./scripts/generate-llms.sh

# Staging config
CONFIG_FILE=/etc/llms-generator/staging.conf ./scripts/generate-llms.sh
```

### Parallel Generation

Edit `generate-llms.sh` to use GNU parallel:

```bash
# Install parallel
sudo apt install parallel

# Modify script to use parallel
parallel -j 4 generate_for_website ::: "${WEBSITES[@]}"
```

### Custom Hooks

Add hooks in scripts for custom actions:

```bash
# After generation hook
if [ -f "$SCRIPT_DIR/hooks/post-generate.sh" ]; then
    source "$SCRIPT_DIR/hooks/post-generate.sh"
fi
```

---

## 🎯 Next Steps

- **Monitor**: Setup health checks and alerts
- **Backup**: Configure automated backups
- **Scale**: Add more websites to configuration
- **Optimize**: Adjust generation settings per domain

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub.
