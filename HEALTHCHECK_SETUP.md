# Health Check & Auto-Restart Setup

This guide explains how to set up automatic health monitoring and restart for the LLMs.txt Generator.

## Overview

The health check script monitors:
- ✅ Frontend (Next.js) on port 5001
- ✅ Backend (FastAPI) on port 8000
- ✅ HTTP endpoint responses
- ✅ Automatic restart if services are down

## Installation

### 1. Copy Health Check Script to Server

```bash
# On your local machine
scp healthcheck.sh root@your-server:/opt/ai-llmstxt-generator/

# Or on the server after git pull
cd /opt/ai-llmstxt-generator
chmod +x healthcheck.sh
```

### 2. Create Log Directory

```bash
sudo touch /var/log/llm-txt-healthcheck.log
sudo chmod 666 /var/log/llm-txt-healthcheck.log
```

### 3. Test the Script Manually

```bash
cd /opt/ai-llmstxt-generator
./healthcheck.sh
```

Check the log:
```bash
tail -20 /var/log/llm-txt-healthcheck.log
```

## Crontab Setup

### Option 1: Every 5 Minutes (Recommended)

```bash
sudo crontab -e
```

Add this line:
```cron
*/5 * * * * /opt/ai-llmstxt-generator/healthcheck.sh
```

### Option 2: Every 10 Minutes (Less Aggressive)

```cron
*/10 * * * * /opt/ai-llmstxt-generator/healthcheck.sh
```

### Option 3: Every Hour (Minimal)

```cron
0 * * * * /opt/ai-llmstxt-generator/healthcheck.sh
```

### Save and Exit

- **nano**: `Ctrl+X`, then `Y`, then `Enter`
- **vim**: `Esc`, then `:wq`, then `Enter`

### Verify Crontab

```bash
sudo crontab -l
```

## How It Works

### Health Checks Performed

1. **Port Check**: Verifies ports 5001 and 8000 are listening
2. **HTTP Check**: Tests actual HTTP responses from:
   - Frontend: `http://localhost:5001/llm-text-generator`
   - Backend: `http://localhost:8000/docs`
3. **Auto-Restart**: If any check fails, stops and restarts both services
4. **Verification**: After restart, verifies services are healthy

### Restart Process

1. Kill all Next.js and uvicorn processes
2. Wait 2 seconds
3. Start backend (uvicorn with 600s timeout)
4. Wait 5 seconds
5. Start frontend (production mode)
6. Wait 10 seconds
7. Verify services are responding

## Monitoring

### View Recent Logs

```bash
tail -50 /var/log/llm-txt-healthcheck.log
```

### Watch Logs in Real-Time

```bash
tail -f /var/log/llm-txt-healthcheck.log
```

### Check for Restarts Today

```bash
grep "RESTARTING SERVICES" /var/log/llm-txt-healthcheck.log | grep "$(date +%Y-%m-%d)"
```

### Count Restarts This Week

```bash
grep "RESTARTING SERVICES" /var/log/llm-txt-healthcheck.log | wc -l
```

## Log Rotation

To prevent the log file from growing too large:

```bash
sudo nano /etc/logrotate.d/llm-txt-healthcheck
```

Add:
```
/var/log/llm-txt-healthcheck.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Troubleshooting

### Script Not Running

**Check crontab:**
```bash
sudo crontab -l
```

**Check cron service:**
```bash
sudo systemctl status cron
```

**Check syslog for cron errors:**
```bash
sudo grep CRON /var/log/syslog | tail -20
```

### Services Keep Restarting

**Check if there's a real issue:**
```bash
# Test frontend manually
curl -I http://localhost:5001/llm-text-generator

# Test backend manually
curl -I http://localhost:8000/docs

# Check process status
ps aux | grep -E "(next|uvicorn)"
```

**Check application logs:**
```bash
# Nginx logs
sudo tail -50 /var/log/nginx/obviousworks.ch/error.log

# Application logs (if redirected)
tail -50 /var/log/llm-txt-healthcheck.log
```

### Manual Restart Still Needed

If the health check script can't fix the issue:

```bash
cd /opt/ai-llmstxt-generator

# Stop everything
pkill -9 -f "next"
pkill -9 -f "uvicorn"

# Rebuild if needed
rm -rf .next
npm run build

# Start manually
./start-production.sh
```

## Customization

### Change Check Frequency

Edit the crontab timing:
- `*/5 * * * *` = Every 5 minutes
- `*/15 * * * *` = Every 15 minutes
- `0 * * * *` = Every hour
- `0 */2 * * *` = Every 2 hours

### Change Timeout Values

Edit `healthcheck.sh`:
```bash
# Line with curl --max-time
curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$url"
```

### Add Email Notifications

Install mailutils:
```bash
sudo apt-get install mailutils
```

Add to `healthcheck.sh` after restart:
```bash
if $RESTART_NEEDED; then
    echo "Services restarted at $(date)" | mail -s "LLM Service Restart" your@email.com
fi
```

## Best Practices

- ✅ Monitor the log file regularly
- ✅ Set up log rotation to prevent disk space issues
- ✅ Check for patterns in restart times (might indicate underlying issues)
- ✅ Keep the health check interval reasonable (5-10 minutes recommended)
- ✅ Test the script manually after any changes

## Disable Health Check

To temporarily disable:
```bash
sudo crontab -e
# Comment out the line with #
# */5 * * * * /opt/ai-llmstxt-generator/healthcheck.sh
```

To permanently remove:
```bash
sudo crontab -e
# Delete the line completely
```

## Summary

The health check script provides:
- 🔄 Automatic monitoring every 5 minutes (configurable)
- 🚨 Detects when services are down or unresponsive
- 🔧 Automatically restarts failed services
- 📝 Logs all checks and restarts
- ✅ Verifies restart was successful

This ensures maximum uptime with minimal manual intervention!
