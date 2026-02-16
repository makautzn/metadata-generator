/**
 * ResultTile — displays a single file processing result as a card.
 *
 * Shows file name, type badge, processing time, and content area.
 * Error tiles are visually distinct with a red-tinted border.
 */
import { Badge, Card } from '@/components/ui';
import type { ProcessingFile } from '@/lib/types';
import type { ReactNode } from 'react';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ResultTileProps {
  /** The processed file to display */
  file: ProcessingFile;
  /** Optional children rendered inside the content area (metadata details from Task 011) */
  children?: ReactNode;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTime(ms: number | null): string {
  if (ms === null) return '';
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

function typeLabel(fileType: ProcessingFile['fileType']): string {
  switch (fileType) {
    case 'image':
      return 'Bild';
    case 'audio':
      return 'Audio';
    default:
      return 'Datei';
  }
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ResultTile({ file, children }: ResultTileProps) {
  const isError = file.status === 'error';

  const header = (
    <div className="flex items-center gap-2">
      <span className="flex-1 truncate" title={file.fileName}>
        {file.fileName}
      </span>
      <Badge variant={file.fileType === 'image' ? 'primary' : 'default'}>
        {typeLabel(file.fileType)}
      </Badge>
      {file.processingTimeMs !== null && (
        <span className="whitespace-nowrap text-xs text-[#9ca3af]">
          {formatTime(file.processingTimeMs)}
        </span>
      )}
    </div>
  );

  if (isError) {
    return (
      <div data-testid={`tile-${file.fileIndex}`}>
        <Card header={header} className="border-red-300 bg-red-50">
          <p className="text-sm text-red-700" data-testid="tile-error-message">
            {file.error ?? 'Ein unbekannter Fehler ist aufgetreten.'}
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div data-testid={`tile-${file.fileIndex}`}>
      <Card header={header}>
        {children ?? (
          <p className="text-sm text-[#9ca3af]" data-testid="tile-placeholder">
            Metadaten werden in einer zukünftigen Version angezeigt.
          </p>
        )}
      </Card>
    </div>
  );
}
