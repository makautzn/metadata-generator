/**
 * Tests for the TileGrid component.
 */
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { TileGrid } from '@/components/TileGrid';
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
    processingTimeMs: 100,
    fileIndex: 0,
    thumbnailUrl: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('TileGrid', () => {
  it('renders nothing when files list is empty', () => {
    const { container } = render(<TileGrid files={[]} />);
    expect(container.innerHTML).toBe('');
  });

  it('renders grid container with CSS grid properties', () => {
    render(<TileGrid files={[makeFile()]} />);
    const grid = screen.getByTestId('tile-grid');
    expect(grid).toBeInTheDocument();
    expect(grid.style.gridTemplateColumns).toBe('repeat(auto-fill, minmax(320px, 1fr))');
  });

  it('renders tiles in upload order by file_index', () => {
    const files = [
      makeFile({ id: 'c', fileName: 'third.jpg', fileIndex: 2 }),
      makeFile({ id: 'a', fileName: 'first.jpg', fileIndex: 0 }),
      makeFile({ id: 'b', fileName: 'second.jpg', fileIndex: 1 }),
    ];
    render(<TileGrid files={files} />);

    const tiles = screen.getAllByTestId(/^tile-\d+$/);
    expect(tiles).toHaveLength(3);
    expect(tiles[0]).toHaveAttribute('data-testid', 'tile-0');
    expect(tiles[1]).toHaveAttribute('data-testid', 'tile-1');
    expect(tiles[2]).toHaveAttribute('data-testid', 'tile-2');
  });

  it('renders correct number of tiles', () => {
    const files = [
      makeFile({ id: 'a', fileIndex: 0 }),
      makeFile({ id: 'b', fileIndex: 1 }),
      makeFile({ id: 'c', fileIndex: 2 }),
    ];
    render(<TileGrid files={files} />);
    expect(screen.getAllByTestId(/^tile-\d+$/)).toHaveLength(3);
  });

  it('passes renderContent to tiles', () => {
    render(
      <TileGrid
        files={[makeFile()]}
        renderContent={(f) => <span data-testid="custom">Custom: {f.fileName}</span>}
      />,
    );
    expect(screen.getByTestId('custom')).toHaveTextContent('Custom: photo.jpg');
  });
});
