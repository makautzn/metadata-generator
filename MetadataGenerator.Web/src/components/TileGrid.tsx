/**
 * TileGrid — responsive CSS Grid container for result tiles.
 *
 * Renders ProcessingFile entries as ResultTile cards sorted by file_index.
 * Uses CSS Grid auto-fill with a minimum column width of 320px.
 */
import { ResultTile } from '@/components/ResultTile';
import type { ProcessingFile } from '@/lib/types';
import type { ReactNode } from 'react';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface TileGridProps {
  /** Processed files to display as tiles */
  files: ProcessingFile[];
  /** Optional render function for tile content (metadata details from Task 011) */
  renderContent?: (file: ProcessingFile) => ReactNode;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function TileGrid({ files, renderContent }: TileGridProps) {
  if (files.length === 0) return null;

  // Sort by file_index to maintain upload order
  const sorted = [...files].sort((a, b) => a.fileIndex - b.fileIndex);

  return (
    <div
      className="grid w-full gap-4"
      style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}
      data-testid="tile-grid"
    >
      {sorted.map((file) => (
        <ResultTile key={file.id} file={file}>
          {renderContent?.(file)}
        </ResultTile>
      ))}
    </div>
  );
}
