/**
 * Tests for the ResultTile component.
 */
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ResultTile } from '@/components/ResultTile';
import type { ProcessingFile } from '@/lib/types';

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
    metadata: null,
    error: null,
    processingTimeMs: 450,
    fileIndex: 0,
    thumbnailUrl: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ResultTile', () => {
  it('renders file name in the header', () => {
    render(<ResultTile file={makeFile()} />);
    expect(screen.getByText('photo.jpg')).toBeInTheDocument();
  });

  it('renders type badge for image file', () => {
    render(<ResultTile file={makeFile({ fileType: 'image' })} />);
    expect(screen.getByText('Bild')).toBeInTheDocument();
  });

  it('renders type badge for audio file', () => {
    render(<ResultTile file={makeFile({ fileType: 'audio' })} />);
    expect(screen.getByText('Audio')).toBeInTheDocument();
  });

  it('displays processing time in ms', () => {
    render(<ResultTile file={makeFile({ processingTimeMs: 320 })} />);
    expect(screen.getByText('320 ms')).toBeInTheDocument();
  });

  it('displays processing time in seconds for large values', () => {
    render(<ResultTile file={makeFile({ processingTimeMs: 2500 })} />);
    expect(screen.getByText('2.5 s')).toBeInTheDocument();
  });

  it('renders children content when provided', () => {
    render(
      <ResultTile file={makeFile()}>
        <p>Custom metadata content</p>
      </ResultTile>,
    );
    expect(screen.getByText('Custom metadata content')).toBeInTheDocument();
  });

  it('renders placeholder text when no children', () => {
    render(<ResultTile file={makeFile()} />);
    expect(screen.getByTestId('tile-placeholder')).toBeInTheDocument();
  });

  it('renders error tile with error message', () => {
    render(
      <ResultTile file={makeFile({ status: 'error', error: 'File corrupt', fileIndex: 3 })} />,
    );
    expect(screen.getByTestId('tile-error-message')).toHaveTextContent('File corrupt');
  });

  it('error tile has red styling', () => {
    const { container } = render(
      <ResultTile file={makeFile({ status: 'error', error: 'Bad format', fileIndex: 2 })} />,
    );
    // The Card wrapper should have red border and background classes
    const card = container.querySelector('.border-red-300');
    expect(card).toBeInTheDocument();
  });

  it('wraps in a testid with fileIndex', () => {
    render(<ResultTile file={makeFile({ fileIndex: 5 })} />);
    expect(screen.getByTestId('tile-5')).toBeInTheDocument();
  });
});
