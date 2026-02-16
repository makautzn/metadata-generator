/**
 * ProgressList — shows per-file processing status and overall progress summary.
 *
 * Displays a spinner for processing files, a checkmark for completed,
 * and an error icon for failed files.
 */
'use client';

import type { ProcessingFile } from '@/lib/types';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ProgressListProps {
  /** Files currently being tracked */
  files: ProcessingFile[];
}

// ---------------------------------------------------------------------------
// Status icons
// ---------------------------------------------------------------------------

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin text-[#1a56db]"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      data-testid="spinner"
      role="img"
      aria-label="Wird verarbeitet"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

function Checkmark() {
  return (
    <svg
      className="h-4 w-4 text-green-600"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      data-testid="checkmark"
      role="img"
      aria-label="Erfolgreich"
    >
      <path
        fillRule="evenodd"
        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg
      className="h-4 w-4 text-red-600"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      data-testid="error-icon"
      role="img"
      aria-label="Fehler"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function StatusIcon({ status }: { status: ProcessingFile['status'] }) {
  switch (status) {
    case 'pending':
    case 'processing':
      return <Spinner />;
    case 'success':
      return <Checkmark />;
    case 'error':
      return <ErrorIcon />;
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ProgressList({ files }: ProgressListProps) {
  if (files.length === 0) return null;

  const completed = files.filter((f) => f.status === 'success' || f.status === 'error').length;

  return (
    <div className="w-full space-y-3" data-testid="progress-list">
      {/* Overall progress summary */}
      <p className="text-sm font-medium text-[#374151]" data-testid="progress-summary">
        {completed} von {files.length} Dateien verarbeitet
      </p>

      {/* Per-file list */}
      <ul className="divide-y divide-[#e5e7eb] rounded-lg border border-[#e5e7eb]">
        {files.map((pf) => (
          <li key={pf.id} className="flex items-center gap-3 px-3 py-2 text-sm">
            <StatusIcon status={pf.status} />
            <span className="flex-1 truncate text-[#374151]" title={pf.fileName}>
              {pf.fileName}
            </span>
            {pf.status === 'error' && pf.error && (
              <span className="text-xs text-red-600" data-testid={`error-msg-${pf.id}`}>
                {pf.error}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
