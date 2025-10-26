/**
 * Export to Google Sheets Button Component
 * Allows users to export simulation results to their Google Drive
 */

import { useState } from 'react';
import { simulationsService } from '../services/simulations';

interface ExportToSheetsButtonProps {
  simulationId: string;
  simulationName?: string;
}

export function ExportToSheetsButton({ simulationId, simulationName }: ExportToSheetsButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [spreadsheetUrl, setSpreadsheetUrl] = useState<string | null>(null);

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setSpreadsheetUrl(null);

    try {
      console.log(`📊 Exporting simulation ${simulationId} to Google Sheets...`);
      
      const result = await simulationsService.exportToSheets(simulationId);
      
      console.log('✅ Export successful:', result);
      
      setSuccess(result.message || 'Exported to Google Sheets!');
      setSpreadsheetUrl(result.spreadsheet_url);
    } catch (err: any) {
      console.error('❌ Export failed:', err);
      
      // Handle different error types
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Please log in with Google to export');
      } else if (err.response?.status === 401) {
        setError('Your Google session expired. Please log in again with Google.');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(err.message || 'Failed to export to Google Sheets');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div>
        <button
          onClick={handleExport}
          disabled={loading || !!spreadsheetUrl}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium shadow-sm"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Exporting to Google Sheets...</span>
            </>
          ) : spreadsheetUrl ? (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>Exported!</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>📊 Export to Google Sheets</span>
            </>
          )}
        </button>
        
        {!loading && !spreadsheetUrl && (
          <p className="text-xs text-gray-500 mt-1 text-center">
            Creates a formatted spreadsheet in your Google Drive
          </p>
        )}
      </div>

      {success && spreadsheetUrl && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-green-800">{success}</p>
              <a
                href={spreadsheetUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 mt-2 text-sm text-green-700 hover:text-green-900 font-medium underline"
              >
                📊 Open in Google Sheets
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
              <button
                onClick={() => {
                  setSuccess(null);
                  setSpreadsheetUrl(null);
                }}
                className="block mt-2 text-xs text-green-600 hover:text-green-800 underline"
              >
                Export again
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">Failed to export</p>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              {error.includes('log in') && (
                <button
                  onClick={() => window.location.reload()}
                  className="mt-2 text-sm text-red-700 hover:text-red-900 underline font-medium"
                >
                  Refresh and log in with Google
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

