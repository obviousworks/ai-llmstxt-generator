# Google Analytics 4 - Testing & Verification Guide

## 🚀 Application is Running

**Frontend:** http://localhost:5001  
**Backend API:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

## 📊 How to See Events in Google Analytics

### Method 1: Real-time Reports (Recommended for Testing)

1. **Open Google Analytics**
   - Go to: https://analytics.google.com
   - Select your property with Measurement ID `G-3MWJERVHBJ`

2. **Navigate to Real-time Reports**
   - Click **Reports** in the left sidebar
   - Click **Realtime** (or **Real-time**)
   - You'll see a dashboard showing live activity

3. **What You'll See**
   - **Active Users**: Number of users currently on your site (should show "1" when you're testing)
   - **Event count by Event name**: List of all events being triggered
   - **Users by Page title and screen name**: Which pages are being viewed

4. **Test the Events**
   - Open http://localhost:5001 in your browser
   - Wait 10-30 seconds for the page_view event to appear
   - Enter a URL (e.g., `https://docs.anthropic.com`)
   - Click "Generate llms.txt (Summary)"
   - Watch the Real-time dashboard - you should see:
     - `llms_generation_started` event
     - After generation completes: `llms_generation_success` event
     - When you download: `file_download` event

### Method 2: DebugView (Best for Development)

1. **Enable Debug Mode**
   - Open your browser's Developer Console (F12)
   - Paste this command:
   ```javascript
   window.gtag('config', 'G-3MWJERVHBJ', { debug_mode: true });
   ```
   - Refresh the page

2. **Open DebugView in Google Analytics**
   - In Google Analytics, click **Configure** (gear icon) in the left sidebar
   - Click **DebugView**
   - You'll see a real-time stream of events with full details

3. **What You'll See**
   - Every event with all its parameters
   - Event timestamps
   - User properties
   - Much more detailed than Real-time reports

### Method 3: Browser DevTools (Immediate Verification)

1. **Open Browser DevTools**
   - Press F12 or right-click → Inspect
   - Go to the **Network** tab
   - Filter by: `google-analytics.com` or `gtag`

2. **Test Events**
   - Perform actions in the app
   - You'll see network requests to Google Analytics
   - Click on a request to see the payload with event data

3. **What to Look For**
   - Requests to `https://www.google-analytics.com/g/collect`
   - Query parameters containing your event data
   - Status 200 = events sent successfully

### Method 4: Google Analytics Debugger Extension

1. **Install Extension**
   - Chrome: [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna)
   - Firefox: [GA Debugger](https://addons.mozilla.org/en-US/firefox/addon/ga-debugger/)

2. **Enable the Extension**
   - Click the extension icon to enable
   - Open browser console (F12)
   - You'll see detailed GA4 logs

3. **What You'll See**
   - All GA4 commands logged to console
   - Event parameters
   - Configuration details

## 🧪 Complete Testing Checklist

### Test Scenario 1: Basic Page View
- [ ] Open http://localhost:5001
- [ ] Check Real-time → Should show 1 active user
- [ ] Check Real-time → Should show `page_view` event

### Test Scenario 2: Generate Summary
- [ ] Enter URL: `https://docs.anthropic.com`
- [ ] Click "Generate llms.txt (Summary)"
- [ ] Check Real-time → Should show `llms_generation_started` event
- [ ] Wait for generation to complete
- [ ] Check Real-time → Should show `llms_generation_success` event
- [ ] Verify event parameters:
  - `url`: https://docs.anthropic.com
  - `generation_type`: summary
  - `pages_analyzed`: (number)
  - `generation_time`: (seconds)

### Test Scenario 3: Download File
- [ ] After successful generation, click "Download llms.txt (Summary)"
- [ ] Check Real-time → Should show `file_download` event
- [ ] Verify event parameters:
  - `file_name`: llms.txt
  - `url`: https://docs.anthropic.com
  - `file_size`: (bytes)

### Test Scenario 4: Generate Full-text
- [ ] Click "Generate llms-full.txt (All Pages)"
- [ ] Check Real-time → Should show `llms_generation_started` event with `generation_type`: fulltext
- [ ] Wait for completion
- [ ] Check Real-time → Should show `llms_generation_success` event

### Test Scenario 5: Error Handling
- [ ] Enter invalid URL: `not-a-valid-url`
- [ ] Click generate
- [ ] Check Real-time → Should show `llms_generation_error` event
- [ ] Verify event parameters include `error_message`

### Test Scenario 6: Existing Files Dialog
- [ ] Enter URL of a site with existing llms.txt (if any)
- [ ] Check Real-time → Should show `existing_files_found` event
- [ ] Click one of the dialog buttons
- [ ] Check Real-time → Should show `existing_files_choice` event

## 📈 Viewing Historical Data (After 24-48 Hours)

After events have been collected for a day or two:

### 1. Standard Reports
- **Reports → Engagement → Events**
  - See all custom events
  - Event counts
  - Top events

### 2. Exploration Reports
- **Explore → Create new exploration**
- **Free form exploration** for custom analysis

### Example Explorations:

**Most Analyzed URLs:**
```
Dimensions: url (event parameter)
Metrics: Event count
Filter: Event name = llms_generation_started
```

**Success Rate:**
```
Metrics: 
  - Event count (llms_generation_success)
  - Event count (llms_generation_error)
Calculate: Success rate = success / (success + error)
```

**Average Generation Time:**
```
Dimension: generation_type
Metric: Average of generation_time parameter
Filter: Event name = llms_generation_success
```

## 🔍 Troubleshooting

### Events Not Showing Up?

1. **Check Measurement ID**
   ```bash
   # Verify in .env file
   cat .env | grep GA_MEASUREMENT_ID
   ```
   Should show: `NEXT_PUBLIC_GA_MEASUREMENT_ID=G-3MWJERVHBJ`

2. **Check Browser Console**
   - Open DevTools (F12)
   - Look for errors related to gtag or analytics
   - Should see: `window.dataLayer` is defined

3. **Disable Ad Blockers**
   - Ad blockers often block Google Analytics
   - Temporarily disable for testing

4. **Check Network Tab**
   - DevTools → Network tab
   - Filter: `google-analytics.com`
   - Should see requests with status 200

5. **Wait Time**
   - Real-time data can take 10-30 seconds to appear
   - DebugView is faster (near-instant)

### Common Issues

**Issue:** "No active users" in Real-time
- **Solution:** Refresh the page, wait 30 seconds

**Issue:** Events show in Network tab but not in GA
- **Solution:** Check if you're looking at the correct property in GA

**Issue:** TypeScript errors
- **Solution:** Run `npm run build` to check for compilation errors

## 📱 Testing on Different Devices

### Desktop Browser
- Open http://localhost:5001
- Follow test scenarios above

### Mobile Device (Same Network)
- Find your local IP: `ifconfig | grep "inet "`
- Open http://192.168.178.34:5001 on mobile
- Events will show in same GA property

### Incognito/Private Mode
- Test without browser extensions
- Verify tracking works in clean environment

## 🎯 Expected Event Flow

```
User visits site
  ↓
page_view (automatic)
  ↓
User enters URL and clicks generate
  ↓
llms_generation_started
  ↓
Generation completes successfully
  ↓
llms_generation_success
  ↓
User clicks download
  ↓
file_download
```

## 📊 Real-time Dashboard Screenshot Guide

When you open Real-time in Google Analytics, you should see:

1. **Top Section**: Active users (shows "1" when you're testing)
2. **Event count by Event name**: Bar chart showing:
   - page_view
   - llms_generation_started
   - llms_generation_success
   - file_download
   - etc.
3. **Users by Page title**: Shows which pages users are on
4. **Event count by Page title and screen name**: Events per page

## 🔗 Quick Links

- **Google Analytics Dashboard**: https://analytics.google.com
- **Real-time Reports**: Analytics → Reports → Realtime
- **DebugView**: Analytics → Configure → DebugView
- **Events Report**: Analytics → Reports → Engagement → Events
- **GA4 Documentation**: https://support.google.com/analytics/answer/9216061

## 💡 Pro Tips

1. **Keep Real-time Open**: Open GA Real-time in one browser tab, your app in another
2. **Use DebugView for Development**: More detailed than Real-time
3. **Check Network Tab First**: Fastest way to verify events are being sent
4. **Test in Incognito**: Avoid interference from browser extensions
5. **Wait 24-48 Hours**: For full historical reports and explorations

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Real-time shows your active session
- ✅ Events appear within 30 seconds of actions
- ✅ Event parameters contain correct data
- ✅ Network tab shows successful requests to google-analytics.com
- ✅ No console errors related to gtag

---

**Need Help?** Check the main [GOOGLE_ANALYTICS_SETUP.md](./GOOGLE_ANALYTICS_SETUP.md) for more details.
