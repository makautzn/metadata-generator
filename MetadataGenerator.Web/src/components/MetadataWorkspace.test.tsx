/**
 * Tests for the MetadataWorkspace orchestrator component.
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MetadataWorkspace } from '@/components/MetadataWorkspace';
import type { BatchAnalysisResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Mock api-client
// ---------------------------------------------------------------------------

const mockUploadFile = vi.fn();

vi.mock('@/lib/api-client', () => ({
  uploadFile: (...args: unknown[]) => mockUploadFile(...args),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createImageFile(name: string = 'photo.jpg', size: number = 1024): File {
  const file = new File(['x'.repeat(size)], name, { type: 'image/jpeg' });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

function makeSuccessResponse(fileNames: string[]): BatchAnalysisResponse {
  return {
    results: fileNames.map((name, i) => ({
      file_name: name,
      file_index: i,
      status: 'success' as const,
      file_type: name.endsWith('.mp3') ? ('audio' as const) : ('image' as const),
      metadata: {
        file_name: name,
        file_size: 1024,
        mime_type: 'image/jpeg',
        description: `Description of ${name}`,
        keywords: ['test'],
        caption: `Caption for ${name}`,
        exif: {},
        processing_time_ms: 250,
      },
      error: null,
    })),
    total_files: fileNames.length,
    successful: fileNames.length,
    failed: 0,
    total_processing_time_ms: 500,
  };
}

function makeMixedResponse(): BatchAnalysisResponse {
  return {
    results: [
      {
        file_name: 'good.jpg',
        file_index: 0,
        status: 'success' as const,
        file_type: 'image' as const,
        metadata: {
          file_name: 'good.jpg',
          file_size: 1024,
          mime_type: 'image/jpeg',
          description: 'A photo',
          keywords: ['photo'],
          caption: 'A nice photo',
          exif: {},
          processing_time_ms: 200,
        },
        error: null,
      },
      {
        file_name: 'bad.jpg',
        file_index: 1,
        status: 'error' as const,
        file_type: 'image' as const,
        metadata: null,
        error: { detail: 'Processing failed', error_code: 'ANALYSIS_ERROR' },
      },
    ],
    total_files: 2,
    successful: 1,
    failed: 1,
    total_processing_time_ms: 300,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('MetadataWorkspace', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts in idle phase with FileUpload visible', () => {
    render(<MetadataWorkspace />);
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
  });

  it('transitions to processing phase on upload start', async () => {
    // API call that never resolves (simulates ongoing processing)
    mockUploadFile.mockReturnValue(new Promise(() => {}));

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    const file = createImageFile('test.jpg');

    await userEvent.upload(input, file);
    await userEvent.click(screen.getByTestId('analyze-button'));

    // Should show progress list with processing state
    await waitFor(() => {
      expect(screen.getByTestId('progress-list')).toBeInTheDocument();
    });
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
    expect(screen.getByText('test.jpg')).toBeInTheDocument();
  });

  it('shows progress summary during processing', async () => {
    mockUploadFile.mockReturnValue(new Promise(() => {}));

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, [createImageFile('a.jpg'), createImageFile('b.jpg')]);
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('progress-summary')).toHaveTextContent(
        '0 von 2 Dateien verarbeitet',
      );
    });
  });

  it('transitions to done phase with tile grid on success', async () => {
    mockUploadFile.mockResolvedValue({
      ok: true,
      data: makeSuccessResponse(['photo.jpg']),
    });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, createImageFile('photo.jpg'));
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('tile-grid')).toBeInTheDocument();
    });
    expect(screen.getByTestId('tile-0')).toBeInTheDocument();
    // File name appears in both ProgressList and ResultTile
    expect(screen.getAllByText('photo.jpg').length).toBeGreaterThanOrEqual(1);
  });

  it('shows error tiles for failed files in mixed response', async () => {
    mockUploadFile.mockResolvedValue({ ok: true, data: makeMixedResponse() });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, [createImageFile('good.jpg'), createImageFile('bad.jpg')]);
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('tile-grid')).toBeInTheDocument();
    });
    expect(screen.getByTestId('tile-error-message')).toHaveTextContent('Processing failed');
  });

  it('updates progress summary in done phase', async () => {
    mockUploadFile.mockResolvedValue({
      ok: true,
      data: makeSuccessResponse(['a.jpg', 'b.jpg']),
    });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, [createImageFile('a.jpg'), createImageFile('b.jpg')]);
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('progress-summary')).toHaveTextContent(
        '2 von 2 Dateien verarbeitet',
      );
    });
  });

  it('shows global error banner on upload failure', async () => {
    mockUploadFile.mockResolvedValue({
      ok: false,
      error: { error_code: 'SERVER_ERROR', message: 'Internal server error' },
    });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, createImageFile('fail.jpg'));
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('global-error')).toHaveTextContent('Internal server error');
    });
  });

  it('allows restarting with new files via restart button', async () => {
    mockUploadFile.mockResolvedValue({
      ok: true,
      data: makeSuccessResponse(['photo.jpg']),
    });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, createImageFile('photo.jpg'));
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(screen.getByTestId('restart-button')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByTestId('restart-button'));

    // Should be back to idle with upload zone
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
  });

  it('state updates correctly when API response maps to files', async () => {
    mockUploadFile.mockResolvedValue({ ok: true, data: makeMixedResponse() });

    render(<MetadataWorkspace />);
    const input = screen.getByTestId('file-input');
    await userEvent.upload(input, [createImageFile('good.jpg'), createImageFile('bad.jpg')]);
    await userEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      // 2 of 2 processed (1 success + 1 error)
      expect(screen.getByTestId('progress-summary')).toHaveTextContent(
        '2 von 2 Dateien verarbeitet',
      );
    });
    // Success tile and error tile both present
    expect(screen.getByTestId('tile-0')).toBeInTheDocument();
    expect(screen.getByTestId('tile-1')).toBeInTheDocument();
  });
});
