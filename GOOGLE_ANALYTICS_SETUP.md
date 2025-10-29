# Google Analytics 4 (GA4) Integration

This document describes the Google Analytics 4 tracking implementation for the LLMs.txt Generator application.

## Overview

The application tracks user interactions and generation events to help understand:
- Which websites are generating llms.txt files
- How often the service is used
- Success vs. error rates
- User behavior patterns

## Configuration

### Environment Variable

Add your Google Analytics Measurement ID to your `.env` file:

```bash
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-3MWJERVHBJ
```

The Measurement ID is already set to `G-3MWJERVHBJ` as the default fallback in the layout.

### Getting Your Measurement ID

1. Go to [Google Analytics](https://analytics.google.com)
2. Navigate to **Admin** → **Data Streams**
3. Select your web stream
4. Copy the **Measurement ID** (format: `G-XXXXXXXXXX`)

## Tracked Events

### 1. Page Views (Automatic)
- Automatically tracked on all page loads
- Standard GA4 page_view event

### 2. Generation Started
**Event Name:** `llms_generation_started`

Triggered when a user submits a URL for generation.

**Parameters:**
- `event_category`: "Generation"
- `event_label`: "summary" | "fulltext"
- `url`: The website URL being analyzed
- `generation_type`: "summary" | "fulltext"

### 3. Generation Success
**Event Name:** `llms_generation_success`

Triggered when generation completes successfully.

**Parameters:**
- `event_category`: "Generation"
- `event_label`: "summary" | "fulltext"
- `url`: The website URL analyzed
- `generation_type`: "summary" | "fulltext"
- `pages_analyzed`: Number of pages processed
- `generation_time`: Time taken in seconds
- `ai_enhanced`: Whether AI enhancement was used

### 4. Generation Error
**Event Name:** `llms_generation_error`

Triggered when generation fails.

**Parameters:**
- `event_category`: "Generation"
- `event_label`: "summary" | "fulltext"
- `url`: The website URL attempted
- `generation_type`: "summary" | "fulltext"
- `error_message`: Error description

### 5. File Download
**Event Name:** `file_download`

Triggered when a user downloads a generated file.

**Parameters:**
- `event_category`: "Download"
- `event_label`: Filename ("llms.txt" | "llms-full.txt")
- `url`: The website URL for the downloaded file
- `file_name`: Name of the downloaded file
- `file_size`: Size of the file in bytes

### 6. Existing Files Found
**Event Name:** `existing_files_found`

Triggered when the system detects existing llms.txt files on the target website.

**Parameters:**
- `event_category`: "Generation"
- `event_label`: "existing_files"
- `url`: The website URL
- `files_found`: Comma-separated list of found files
- `files_count`: Number of files found

### 7. Existing Files Choice
**Event Name:** `existing_files_choice`

Triggered when user makes a choice in the existing files dialog.

**Parameters:**
- `event_category`: "Generation"
- `event_label`: User's choice
- `url`: The website URL
- `user_choice`: "regenerate_summary" | "regenerate_fulltext" | "cancel"

## Implementation Files

### Core Files
- **`app/components/GoogleAnalytics.tsx`**: GA4 script component
- **`lib/analytics.ts`**: Event tracking utility functions
- **`app/layout.tsx`**: GA4 integration in root layout
- **`app/page.tsx`**: Event tracking implementation

### Key Functions

```typescript
// Track URL submission
trackUrlSubmission(url: string, generationType: 'summary' | 'fulltext')

// Track successful generation
trackGenerationSuccess(
  url: string,
  generationType: 'summary' | 'fulltext',
  pagesAnalyzed: number,
  generationTime: number,
  aiEnhanced: boolean
)

// Track generation errors
trackGenerationError(
  url: string,
  generationType: 'summary' | 'fulltext',
  errorMessage: string
)

// Track file downloads
trackFileDownload(filename: string, url: string, fileSize: number)

// Track existing files found
trackExistingFilesFound(url: string, filesFound: string[])

// Track user choice for existing files
trackExistingFilesChoice(
  url: string,
  choice: 'regenerate_summary' | 'regenerate_fulltext' | 'cancel'
)
```

## Privacy & GDPR Compliance

The implementation:
- Uses Google Analytics 4 (privacy-focused by default)
- Only tracks anonymous usage data
- Does not collect personally identifiable information (PII)
- Respects user privacy settings

**Note:** For full GDPR compliance in production, consider adding:
- Cookie consent banner
- Privacy policy page
- Option to opt-out of tracking

## Viewing Analytics Data

### In Google Analytics Dashboard

1. **Real-time Reports**: See live user activity
2. **Events**: View all custom events under **Reports** → **Engagement** → **Events**
3. **Custom Reports**: Create reports for specific metrics

### Useful Custom Explorations

Create custom explorations to analyze:
- Most popular websites being analyzed
- Success rate (success events vs. error events)
- Average generation time
- Download conversion rate
- User flow through existing files dialog

### Example Queries

**Most Analyzed URLs:**
- Dimension: `url` (event parameter)
- Metric: Event count
- Event name: `llms_generation_started`

**Success Rate:**
- Compare counts of `llms_generation_success` vs `llms_generation_error`

**Average Generation Time:**
- Metric: Average of `generation_time` parameter
- Event name: `llms_generation_success`

## Testing

### Development Testing

1. Open browser DevTools → Network tab
2. Filter for `google-analytics.com` or `gtag`
3. Perform actions in the app
4. Verify events are being sent

### Real-time Verification

1. Go to Google Analytics → **Reports** → **Realtime**
2. Use the application
3. See events appear in real-time (may take 10-30 seconds)

### Debug Mode

To enable GA4 debug mode, add to browser console:

```javascript
window.gtag('config', 'G-3MWJERVHBJ', { debug_mode: true });
```

Or install the [Google Analytics Debugger Chrome Extension](https://chrome.google.com/webstore/detail/google-analytics-debugger/).

## Troubleshooting

### Events Not Showing Up

1. **Check Measurement ID**: Verify `NEXT_PUBLIC_GA_MEASUREMENT_ID` is correct
2. **Check Browser Console**: Look for GA4 errors
3. **Ad Blockers**: Disable ad blockers for testing
4. **Wait Time**: Real-time data may take 10-30 seconds to appear

### TypeScript Errors

If you see TypeScript errors related to `window.gtag`, the global type declarations in `lib/analytics.ts` should handle this.

## Performance Impact

- **Minimal**: GA4 script loads asynchronously (`strategy="afterInteractive"`)
- **No blocking**: Does not affect page load performance
- **Lightweight**: No additional dependencies added

## Future Enhancements

Consider adding:
- User ID tracking (for logged-in users)
- Enhanced e-commerce tracking
- Custom dimensions for more detailed analysis
- A/B testing integration
- Conversion funnel tracking
