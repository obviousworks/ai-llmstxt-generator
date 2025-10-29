// Google Analytics event tracking utilities

declare global {
  interface Window {
    gtag?: (
      command: 'event' | 'config' | 'js',
      targetId: string,
      config?: Record<string, unknown>
    ) => void
    dataLayer?: unknown[]
  }
}

interface EventParams {
  event_category?: string
  event_label?: string
  value?: number
  [key: string]: unknown
}

/**
 * Send a custom event to Google Analytics
 */
export const trackEvent = (
  eventName: string,
  params?: EventParams
): void => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', eventName, params)
  }
}

/**
 * Track URL submission for llms.txt generation
 */
export const trackUrlSubmission = (url: string, generationType: 'summary' | 'fulltext'): void => {
  trackEvent('llms_generation_started', {
    event_category: 'Generation',
    event_label: generationType,
    url: url,
    generation_type: generationType,
  })
}

/**
 * Track successful generation
 */
export const trackGenerationSuccess = (
  url: string,
  generationType: 'summary' | 'fulltext',
  pagesAnalyzed: number,
  generationTime: number,
  aiEnhanced: boolean
): void => {
  trackEvent('llms_generation_success', {
    event_category: 'Generation',
    event_label: generationType,
    url: url,
    generation_type: generationType,
    pages_analyzed: pagesAnalyzed,
    generation_time: generationTime,
    ai_enhanced: aiEnhanced,
  })
}

/**
 * Track generation errors
 */
export const trackGenerationError = (
  url: string,
  generationType: 'summary' | 'fulltext',
  errorMessage: string
): void => {
  trackEvent('llms_generation_error', {
    event_category: 'Generation',
    event_label: generationType,
    url: url,
    generation_type: generationType,
    error_message: errorMessage,
  })
}

/**
 * Track file downloads
 */
export const trackFileDownload = (
  filename: string,
  url: string,
  fileSize: number
): void => {
  trackEvent('file_download', {
    event_category: 'Download',
    event_label: filename,
    url: url,
    file_name: filename,
    file_size: fileSize,
  })
}

/**
 * Track when existing files are found
 */
export const trackExistingFilesFound = (
  url: string,
  filesFound: string[]
): void => {
  trackEvent('existing_files_found', {
    event_category: 'Generation',
    event_label: 'existing_files',
    url: url,
    files_found: filesFound.join(', '),
    files_count: filesFound.length,
  })
}

/**
 * Track user choice when existing files are found
 */
export const trackExistingFilesChoice = (
  url: string,
  choice: 'regenerate_summary' | 'regenerate_fulltext' | 'cancel'
): void => {
  trackEvent('existing_files_choice', {
    event_category: 'Generation',
    event_label: choice,
    url: url,
    user_choice: choice,
  })
}
