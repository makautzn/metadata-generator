/**
 * ExportButtons — JSON and CSV download buttons for processed results.
 *
 * Generates files client-side using Blob + URL.createObjectURL.
 */
'use client';

import { useCallback } from 'react';
import { Button } from '@/components/ui';
import type { ProcessingFile, ImageMetadataResponse, AudioMetadataResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ExportButtonsProps {
  /** All processed files */
  files: ProcessingFile[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function timestamp(): string {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function triggerDownload(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/** Escape a CSV cell value */
function csvEscape(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n') || value.includes('\r')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function isImageMetadata(
  metadata: ImageMetadataResponse | AudioMetadataResponse,
): metadata is ImageMetadataResponse {
  return 'caption' in metadata;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ExportButtons({ files }: ExportButtonsProps) {
  const successFiles = files.filter((f) => f.status === 'success' && f.metadata);
  const hasResults = successFiles.length > 0;

  const handleJsonExport = useCallback(() => {
    const data = successFiles.map((f) => f.metadata);
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    triggerDownload(blob, `metadata-export-${timestamp()}.json`);
  }, [successFiles]);

  const handleCsvExport = useCallback(() => {
    const headers = [
      'file_name',
      'file_type',
      'description',
      'keywords',
      'caption_or_summary',
      'processing_time_ms',
      'exif_camera',
      'exif_date',
      'exif_gps',
    ];

    const rows = successFiles.map((f) => {
      const m = f.metadata!;
      const captionOrSummary = isImageMetadata(m)
        ? m.caption
        : (m as AudioMetadataResponse).summary;
      const exifCamera = isImageMetadata(m) ? String(m.exif?.Camera ?? '') : '';
      const exifDate = isImageMetadata(m) ? String(m.exif?.Date ?? '') : '';
      const exifGps = isImageMetadata(m) ? String(m.exif?.GPS ?? '') : '';

      return [
        csvEscape(m.file_name),
        csvEscape(f.fileType),
        csvEscape(m.description),
        csvEscape(m.keywords.join('; ')),
        csvEscape(captionOrSummary),
        String(m.processing_time_ms),
        csvEscape(exifCamera),
        csvEscape(exifDate),
        csvEscape(exifGps),
      ].join(',');
    });

    // UTF-8 BOM for Excel compatibility
    const bom = '\uFEFF';
    const csv = bom + [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    triggerDownload(blob, `metadata-export-${timestamp()}.csv`);
  }, [successFiles]);

  return (
    <div className="flex gap-3" data-testid="export-buttons">
      <Button
        variant="secondary"
        disabled={!hasResults}
        onClick={handleJsonExport}
        data-testid="export-json"
      >
        JSON herunterladen
      </Button>
      <Button
        variant="secondary"
        disabled={!hasResults}
        onClick={handleCsvExport}
        data-testid="export-csv"
      >
        CSV herunterladen
      </Button>
    </div>
  );
}
