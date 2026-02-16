/**
 * MetadataWorkspace — orchestrates file upload, processing feedback, and results display.
 *
 * Manages the full lifecycle: file selection → upload → processing → results grid.
 * Uses FileUpload for selection, ProgressList during processing, and TileGrid for results.
 */
'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import type { SelectedFile } from '@/components/FileUpload';
import { ImageTile } from '@/components/ImageTile';
import { AudioTile } from '@/components/AudioTile';
import { ExportButtons } from '@/components/ExportButtons';
import { ProgressList } from '@/components/ProgressList';
import { TileGrid } from '@/components/TileGrid';
import type {
  AudioMetadataResponse,
  BatchAnalysisResponse,
  ImageMetadataResponse,
  ProcessingFile,
} from '@/lib/types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Classify file type from MIME */
function classifyFile(file: File): 'image' | 'audio' | 'unknown' {
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.startsWith('audio/')) return 'audio';
  return 'unknown';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export type WorkspacePhase = 'idle' | 'processing' | 'done';

export function MetadataWorkspace() {
  const [phase, setPhase] = useState<WorkspacePhase>('idle');
  const [processingFiles, setProcessingFiles] = useState<ProcessingFile[]>([]);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const objectUrlsRef = useRef<string[]>([]);

  // Cleanup object URLs on unmount
  useEffect(() => {
    return () => {
      objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    };
  }, []);

  // -- Upload started: create processing entries ----------------------------
  const handleUploadStart = useCallback((files: SelectedFile[]) => {
    setGlobalError(null);
    // Revoke previous object URLs
    objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    const newUrls: string[] = [];

    const entries: ProcessingFile[] = files.map((sf, index) => {
      const fileType = classifyFile(sf.file);
      let thumbnailUrl: string | null = null;
      if (fileType === 'image') {
        thumbnailUrl = URL.createObjectURL(sf.file);
        newUrls.push(thumbnailUrl);
      }
      return {
        id: sf.id,
        fileName: sf.file.name,
        fileType,
        fileSize: sf.file.size,
        status: 'processing' as const,
        metadata: null,
        error: null,
        processingTimeMs: null,
        fileIndex: index,
        thumbnailUrl,
      };
    });
    objectUrlsRef.current = newUrls;
    setProcessingFiles(entries);
    setPhase('processing');
  }, []);

  // -- Results received: map API response to processing files ---------------
  const handleResults = useCallback((response: BatchAnalysisResponse) => {
    setProcessingFiles((prev) => {
      return prev.map((pf) => {
        const result = response.results.find((r) => r.file_index === pf.fileIndex);
        if (!result) return { ...pf, status: 'error' as const, error: 'Kein Ergebnis erhalten' };

        if (result.status === 'success') {
          return {
            ...pf,
            status: 'success' as const,
            metadata: result.metadata,
            fileType: result.file_type,
            processingTimeMs: result.metadata?.processing_time_ms ?? null,
          };
        }

        return {
          ...pf,
          status: 'error' as const,
          error: result.error?.detail ?? 'Verarbeitung fehlgeschlagen',
          fileType: result.file_type,
        };
      });
    });
    setPhase('done');
  }, []);

  // -- Global upload error --------------------------------------------------
  const handleError = useCallback((message: string) => {
    setGlobalError(message);
    setProcessingFiles((prev) =>
      prev.map((pf) => ({ ...pf, status: 'error' as const, error: message })),
    );
    setPhase('done');
  }, []);

  // -- Reset to start over -------------------------------------------------
  const handleReset = useCallback(() => {
    objectUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    objectUrlsRef.current = [];
    setPhase('idle');
    setProcessingFiles([]);
    setGlobalError(null);
  }, []);

  // -- Render metadata content inside tiles ---------------------------------
  const renderTileContent = useCallback((file: ProcessingFile) => {
    if (file.status !== 'success' || !file.metadata) return undefined;

    if (file.fileType === 'image') {
      return (
        <ImageTile
          metadata={file.metadata as ImageMetadataResponse}
          thumbnailUrl={file.thumbnailUrl}
        />
      );
    }

    if (file.fileType === 'audio') {
      return <AudioTile metadata={file.metadata as AudioMetadataResponse} />;
    }

    return undefined;
  }, []);

  // -- Completed files for the tile grid ------------------------------------
  const completedFiles = processingFiles.filter(
    (f) => f.status === 'success' || f.status === 'error',
  );

  return (
    <div className="w-full space-y-8">
      {/* File upload area — visible in idle and processing phases */}
      {phase === 'idle' && (
        <FileUpload
          onUploadStart={handleUploadStart}
          onResults={handleResults}
          onError={handleError}
        />
      )}

      {/* Progress list — visible during processing */}
      {phase === 'processing' && <ProgressList files={processingFiles} />}

      {/* Results phase */}
      {phase === 'done' && (
        <>
          {/* Progress summary at top */}
          <ProgressList files={processingFiles} />

          {/* Global error banner */}
          {globalError && (
            <div
              className="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700"
              role="alert"
              data-testid="global-error"
            >
              {globalError}
            </div>
          )}

          {/* Tile grid */}
          <TileGrid files={completedFiles} renderContent={renderTileContent} />

          {/* Export buttons */}
          <ExportButtons files={completedFiles} />

          {/* Restart button */}
          <div className="flex justify-center">
            <button
              type="button"
              className="text-sm text-[#1a56db] underline hover:text-[#123a95]"
              onClick={handleReset}
              data-testid="restart-button"
            >
              Neue Dateien verarbeiten
            </button>
          </div>
        </>
      )}
    </div>
  );
}
