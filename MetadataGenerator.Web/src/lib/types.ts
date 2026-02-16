/**
 * Shared TypeScript types and interfaces for the Metadata Generator.
 */

/** Supported file types for upload */
export type FileCategory = 'image' | 'audio';

/** Status of a single file's processing */
export type ProcessingStatus = 'pending' | 'uploading' | 'processing' | 'completed' | 'error';

/** Image metadata returned by the API */
export interface ImageMetadata {
  description: string;
  keywords: string[];
  caption: string;
}

/** Audio metadata returned by the API */
export interface AudioMetadata {
  description: string;
  keywords: string[];
  summary: string;
}

/** Union of all metadata types */
export type FileMetadata = ImageMetadata | AudioMetadata;

/** Represents a single uploaded file and its processing state */
export interface UploadedFile {
  id: string;
  file: File;
  category: FileCategory;
  status: ProcessingStatus;
  progress: number;
  metadata: FileMetadata | null;
  error: string | null;
}

/** API error response shape */
export interface ApiError {
  error_code: string;
  message: string;
  detail?: string;
}

/** Health check response */
export interface HealthResponse {
  status: string;
  service: string;
}

/** Generic API result wrapper */
export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: ApiError };

// ---------------------------------------------------------------------------
// Batch analysis response types
// ---------------------------------------------------------------------------

/** Full image metadata response from the API */
export interface ImageMetadataResponse {
  file_name: string;
  file_size: number;
  mime_type: string;
  description: string;
  keywords: string[];
  caption: string;
  exif: Record<string, string | number | null>;
  processing_time_ms: number;
}

/** Full audio metadata response from the API */
export interface AudioMetadataResponse {
  file_name: string;
  file_size: number;
  mime_type: string;
  description: string;
  keywords: string[];
  summary: string;
  duration_seconds: number | null;
  processing_time_ms: number;
}

/** Error details within a batch result */
export interface BatchErrorDetail {
  detail: string;
  error_code: string;
}

/** Per-file result within a batch response */
export interface FileAnalysisResult {
  file_name: string;
  file_index: number;
  status: 'success' | 'error';
  file_type: 'image' | 'audio' | 'unknown';
  metadata: ImageMetadataResponse | AudioMetadataResponse | null;
  error: BatchErrorDetail | null;
}

/** Top-level batch response */
export interface BatchAnalysisResponse {
  results: FileAnalysisResult[];
  total_files: number;
  successful: number;
  failed: number;
  total_processing_time_ms: number;
}

// ---------------------------------------------------------------------------
// Processing state model (Task 010)
// ---------------------------------------------------------------------------

/** Lifecycle status of a file during processing */
export type FileProcessingStatus = 'pending' | 'processing' | 'success' | 'error';

/** Tracks a file through its full processing lifecycle */
export interface ProcessingFile {
  id: string;
  fileName: string;
  fileType: 'image' | 'audio' | 'unknown';
  fileSize: number;
  status: FileProcessingStatus;
  metadata: ImageMetadataResponse | AudioMetadataResponse | null;
  error: string | null;
  processingTimeMs: number | null;
  fileIndex: number;
  /** Object URL for image thumbnail preview */
  thumbnailUrl: string | null;
}
