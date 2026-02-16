/**
 * Tests for the ProgressList component.
 */
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ProgressList } from '@/components/ProgressList';
import type { ProcessingFile } from '@/lib/types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeFile(overrides: Partial<ProcessingFile> = {}): ProcessingFile {
  return {
    id: 'f1',
    fileName: 'photo.jpg',
    fileType: 'image',
    fileSize: 1024,
    status: 'processing',
    metadata: null,
    error: null,
    processingTimeMs: null,
    fileIndex: 0,
    thumbnailUrl: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ProgressList', () => {
  it('renders nothing when files list is empty', () => {
    const { container } = render(<ProgressList files={[]} />);
    expect(container.innerHTML).toBe('');
  });

  it('shows spinner for processing files', () => {
    render(<ProgressList files={[makeFile({ status: 'processing' })]} />);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('shows spinner for pending files', () => {
    render(<ProgressList files={[makeFile({ status: 'pending' })]} />);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('shows checkmark for success files', () => {
    render(<ProgressList files={[makeFile({ status: 'success' })]} />);
    expect(screen.getByTestId('checkmark')).toBeInTheDocument();
  });

  it('shows error icon for error files', () => {
    render(<ProgressList files={[makeFile({ status: 'error', error: 'Something broke' })]} />);
    expect(screen.getByTestId('error-icon')).toBeInTheDocument();
  });

  it('displays error message for failed files', () => {
    render(
      <ProgressList files={[makeFile({ id: 'e1', status: 'error', error: 'Timeout exceeded' })]} />,
    );
    expect(screen.getByTestId('error-msg-e1')).toHaveTextContent('Timeout exceeded');
  });

  it('displays overall progress summary', () => {
    const files = [
      makeFile({ id: 'a', status: 'success', fileIndex: 0 }),
      makeFile({ id: 'b', status: 'processing', fileIndex: 1 }),
      makeFile({ id: 'c', status: 'error', error: 'fail', fileIndex: 2 }),
    ];
    render(<ProgressList files={files} />);
    // 2 of 3 completed (success + error count as completed)
    expect(screen.getByTestId('progress-summary')).toHaveTextContent('2 von 3 Dateien verarbeitet');
  });

  it('shows 0 of N during processing', () => {
    const files = [
      makeFile({ id: 'a', status: 'processing', fileIndex: 0 }),
      makeFile({ id: 'b', status: 'processing', fileIndex: 1 }),
    ];
    render(<ProgressList files={files} />);
    expect(screen.getByTestId('progress-summary')).toHaveTextContent('0 von 2 Dateien verarbeitet');
  });

  it('renders file names in the list', () => {
    render(
      <ProgressList
        files={[
          makeFile({ id: 'a', fileName: 'alpha.jpg', fileIndex: 0 }),
          makeFile({ id: 'b', fileName: 'beta.mp3', fileIndex: 1 }),
        ]}
      />,
    );
    expect(screen.getByText('alpha.jpg')).toBeInTheDocument();
    expect(screen.getByText('beta.mp3')).toBeInTheDocument();
  });
});
