/**
 * Tests for the ExportButtons component.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ExportButtons } from '@/components/ExportButtons';
import type { ImageMetadataResponse, ProcessingFile } from '@/lib/types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeFile(overrides: Partial<ProcessingFile> = {}): ProcessingFile {
  return {
    id: 'f1',
    fileName: 'photo.jpg',
    fileType: 'image',
    fileSize: 2048,
    status: 'success',
    metadata: {
      file_name: 'photo.jpg',
      file_size: 2048,
      mime_type: 'image/jpeg',
      description: 'A sunset photo',
      keywords: ['sunset', 'photo'],
      caption: 'Beautiful sunset',
      exif: { Camera: 'Canon EOS R5', Date: '2024-06-15' },
      processing_time_ms: 450,
    } satisfies ImageMetadataResponse,
    error: null,
    processingTimeMs: 450,
    fileIndex: 0,
    thumbnailUrl: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Mocks — capture blobs passed to createObjectURL
// ---------------------------------------------------------------------------

let capturedBlobs: Blob[] = [];
let downloadedFiles: { download: string }[] = [];

beforeEach(() => {
  capturedBlobs = [];
  downloadedFiles = [];
  vi.restoreAllMocks();

  vi.spyOn(URL, 'createObjectURL').mockImplementation((obj: Blob | MediaSource) => {
    capturedBlobs.push(obj as Blob);
    return `blob:mock-${capturedBlobs.length}`;
  });
  vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

  // Intercept anchor click
  const origCreate = document.createElement.bind(document);
  vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
    const el = origCreate(tag);
    if (tag === 'a') {
      vi.spyOn(el as HTMLAnchorElement, 'click').mockImplementation(() => {
        downloadedFiles.push({ download: (el as HTMLAnchorElement).download });
      });
    }
    return el;
  });
});

// Helper to read blob text
async function readBlob(blob: Blob): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.readAsText(blob);
  });
}

// Helper to read blob as bytes
async function readBlobBytes(blob: Blob): Promise<Uint8Array> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(new Uint8Array(reader.result as ArrayBuffer));
    reader.readAsArrayBuffer(blob);
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ExportButtons', () => {
  it('renders both export buttons', () => {
    render(<ExportButtons files={[makeFile()]} />);
    expect(screen.getByTestId('export-json')).toBeInTheDocument();
    expect(screen.getByTestId('export-csv')).toBeInTheDocument();
  });

  it('disables buttons when no results exist', () => {
    render(<ExportButtons files={[]} />);
    expect(screen.getByTestId('export-json')).toBeDisabled();
    expect(screen.getByTestId('export-csv')).toBeDisabled();
  });

  it('enables buttons when successful results exist', () => {
    render(<ExportButtons files={[makeFile()]} />);
    expect(screen.getByTestId('export-json')).not.toBeDisabled();
    expect(screen.getByTestId('export-csv')).not.toBeDisabled();
  });

  it('disables buttons when all files are errors', () => {
    render(<ExportButtons files={[makeFile({ status: 'error', metadata: null })]} />);
    expect(screen.getByTestId('export-json')).toBeDisabled();
    expect(screen.getByTestId('export-csv')).toBeDisabled();
  });

  it('JSON export creates valid JSON with all results', async () => {
    render(<ExportButtons files={[makeFile()]} />);
    await userEvent.click(screen.getByTestId('export-json'));

    expect(capturedBlobs).toHaveLength(1);
    const content = await readBlob(capturedBlobs[0]!);
    const parsed = JSON.parse(content);
    expect(parsed).toHaveLength(1);
    expect(parsed[0].file_name).toBe('photo.jpg');
    expect(parsed[0].description).toBe('A sunset photo');
  });

  it('JSON file name includes timestamp', async () => {
    render(<ExportButtons files={[makeFile()]} />);
    await userEvent.click(screen.getByTestId('export-json'));

    expect(downloadedFiles).toHaveLength(1);
    expect(downloadedFiles[0]!.download).toMatch(
      /^metadata-export-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.json$/,
    );
  });

  it('CSV export includes UTF-8 BOM prefix', async () => {
    render(<ExportButtons files={[makeFile()]} />);
    await userEvent.click(screen.getByTestId('export-csv'));

    expect(capturedBlobs).toHaveLength(1);
    const bytes = await readBlobBytes(capturedBlobs[0]!);
    // UTF-8 BOM: EF BB BF
    expect(bytes[0]).toBe(0xef);
    expect(bytes[1]).toBe(0xbb);
    expect(bytes[2]).toBe(0xbf);
  });

  it('CSV export has correct headers', async () => {
    render(<ExportButtons files={[makeFile()]} />);
    await userEvent.click(screen.getByTestId('export-csv'));

    const content = await readBlob(capturedBlobs[0]!);
    const lines = content.replace('\uFEFF', '').split('\n');
    expect(lines[0]).toBe(
      'file_name,file_type,description,keywords,caption_or_summary,processing_time_ms,exif_camera,exif_date,exif_gps',
    );
  });

  it('CSV file name includes timestamp', async () => {
    render(<ExportButtons files={[makeFile()]} />);
    await userEvent.click(screen.getByTestId('export-csv'));

    expect(downloadedFiles).toHaveLength(1);
    expect(downloadedFiles[0]!.download).toMatch(/^metadata-export-.*\.csv$/);
  });

  it('CSV properly escapes special characters', async () => {
    const fileWithSpecials = makeFile({
      metadata: {
        file_name: 'test.jpg',
        file_size: 1024,
        mime_type: 'image/jpeg',
        description: 'A photo, with a comma',
        keywords: ['test'],
        caption: 'Caption with "quotes"',
        exif: {},
        processing_time_ms: 100,
      },
    });

    render(<ExportButtons files={[fileWithSpecials]} />);
    await userEvent.click(screen.getByTestId('export-csv'));

    const content = await readBlob(capturedBlobs[0]!);
    expect(content).toContain('"A photo, with a comma"');
    expect(content).toContain('"Caption with ""quotes"""');
  });
});
