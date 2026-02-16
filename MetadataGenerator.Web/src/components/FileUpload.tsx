/**
 * Multi-file upload component with drag-and-drop support.
 *
 * Handles client-side validation (type, size, count) and displays
 * a file list before triggering the batch upload to the backend.
 */
'use client';

import { type DragEvent, useCallback, useRef, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { uploadFile } from '@/lib/api-client';
import type { BatchAnalysisResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MAX_FILES = 20;
const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

const ACCEPTED_TYPES = new Set([
  'image/jpeg',
  'image/png',
  'image/tiff',
  'image/webp',
  'audio/mpeg',
  'audio/wav',
  'audio/x-wav',
  'audio/mp4',
  'audio/x-m4a',
  'audio/ogg',
]);

const IMAGE_TYPES = new Set(['image/jpeg', 'image/png', 'image/tiff', 'image/webp']);

const ACCEPT_STRING = [
  'image/jpeg',
  'image/png',
  'image/tiff',
  'image/webp',
  '.mp3',
  '.wav',
  '.m4a',
  '.ogg',
].join(',');

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SelectedFile {
  id: string;
  file: File;
  error: string | null;
}

export interface FileUploadProps {
  /** Called with batch results once upload completes */
  onResults?: (results: BatchAnalysisResponse) => void;
  /** Called when an upload error occurs */
  onError?: (message: string) => void;
  /** Called when upload starts, with the list of valid files submitted */
  onUploadStart?: (files: SelectedFile[]) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file: File): string | null {
  if (!ACCEPTED_TYPES.has(file.type)) {
    return `Nicht unterstützter Dateityp: ${file.type || 'unbekannt'}`;
  }
  if (IMAGE_TYPES.has(file.type) && file.size > MAX_IMAGE_SIZE_BYTES) {
    return `Datei zu groß (${formatSize(file.size)}). Maximum: 10 MB`;
  }
  return null;
}

let _fileCounter = 0;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function FileUpload({ onResults, onError, onUploadStart }: FileUploadProps) {
  const [files, setFiles] = useState<SelectedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [countError, setCountError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const arr = Array.from(incoming);

    setFiles((prev) => {
      const total = prev.length + arr.length;
      if (total > MAX_FILES) {
        setCountError(`Maximal ${MAX_FILES} Dateien erlaubt. Sie haben ${total} ausgewählt.`);
        return prev;
      }
      setCountError(null);
      const newEntries: SelectedFile[] = arr.map((f) => ({
        id: `file-${++_fileCounter}`,
        file: f,
        error: validateFile(f),
      }));
      return [...prev, ...newEntries];
    });
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
    setCountError(null);
  }, []);

  const clearAll = useCallback(() => {
    setFiles([]);
    setCountError(null);
  }, []);

  // -- Drag handlers -------------------------------------------------------

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        addFiles(e.dataTransfer.files);
      }
    },
    [addFiles],
  );

  // -- Upload handler ------------------------------------------------------

  const validFiles = files.filter((f) => f.error === null);
  const canUpload = validFiles.length > 0 && !uploading;

  const handleUpload = useCallback(async () => {
    if (!canUpload) return;
    setUploading(true);
    onUploadStart?.(validFiles);

    const formData = new FormData();
    for (const sf of validFiles) {
      formData.append('files', sf.file);
    }

    const result = await uploadFile<BatchAnalysisResponse>('/analyze/batch', formData);

    setUploading(false);

    if (result.ok) {
      onResults?.(result.data);
    } else {
      onError?.(result.error.message);
    }
  }, [canUpload, validFiles, onResults, onError, onUploadStart]);

  // -- Render --------------------------------------------------------------

  return (
    <div className="w-full space-y-4">
      {/* Drop zone */}
      <div
        role="button"
        tabIndex={0}
        aria-label="Dateien hochladen"
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors ${
          dragOver
            ? 'border-[#1a56db] bg-[#e8f0fe]'
            : 'border-[#d1d5db] bg-[#f9fafb] hover:border-[#9ca3af]'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        data-testid="drop-zone"
      >
        <p className="text-sm text-[#6b7280]">Dateien hierher ziehen oder klicken zum Auswählen</p>
        <p className="mt-1 text-xs text-[#9ca3af]">
          JPEG, PNG, TIFF, WebP, MP3, WAV, M4A, OGG — max. {MAX_FILES} Dateien
        </p>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT_STRING}
        className="hidden"
        data-testid="file-input"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            addFiles(e.target.files);
            e.target.value = '';
          }
        }}
      />

      {/* Count error */}
      {countError && (
        <p role="alert" className="text-sm text-[#dc2626]">
          {countError}
        </p>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#374151]">
              {files.length} Datei{files.length !== 1 ? 'en' : ''} ausgewählt
            </span>
            <button
              type="button"
              className="text-xs text-[#6b7280] underline hover:text-[#374151]"
              onClick={clearAll}
              data-testid="clear-all"
            >
              Alle entfernen
            </button>
          </div>

          <ul className="divide-y divide-[#e5e7eb] rounded-lg border border-[#e5e7eb]">
            {files.map((sf) => (
              <li key={sf.id} className="flex items-center justify-between px-3 py-2 text-sm">
                <div className="flex items-center gap-2 overflow-hidden">
                  <span className="truncate text-[#374151]" title={sf.file.name}>
                    {sf.file.name}
                  </span>
                  <span className="whitespace-nowrap text-xs text-[#9ca3af]">
                    {formatSize(sf.file.size)}
                  </span>
                  {sf.error && (
                    <span className="whitespace-nowrap text-xs text-[#dc2626]">{sf.error}</span>
                  )}
                </div>
                <button
                  type="button"
                  aria-label={`${sf.file.name} entfernen`}
                  className="ml-2 text-[#9ca3af] hover:text-[#dc2626]"
                  onClick={() => removeFile(sf.id)}
                  data-testid={`remove-${sf.id}`}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload button */}
      {files.length > 0 && (
        <Button
          variant="primary"
          disabled={!canUpload}
          loading={uploading}
          onClick={handleUpload}
          data-testid="analyze-button"
        >
          Verarbeiten
        </Button>
      )}
    </div>
  );
}
