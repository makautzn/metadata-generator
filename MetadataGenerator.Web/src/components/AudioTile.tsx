/**
 * AudioTile — renders audio metadata fields inside a tile card.
 *
 * Shows audio icon, description, keywords (as badges), summary, and duration.
 */
'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui';
import { CopyButton } from '@/components/CopyButton';
import type { AudioMetadataResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface AudioTileProps {
  metadata: AudioMetadataResponse;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DESCRIPTION_TRUNCATE_LENGTH = 200;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '';
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AudioTile({ metadata }: AudioTileProps) {
  const [descExpanded, setDescExpanded] = useState(false);

  const descLong = metadata.description.length > DESCRIPTION_TRUNCATE_LENGTH;
  const displayDesc =
    descLong && !descExpanded
      ? metadata.description.slice(0, DESCRIPTION_TRUNCATE_LENGTH) + '…'
      : metadata.description;

  return (
    <div className="space-y-3" data-testid="audio-tile">
      {/* Audio icon placeholder */}
      <div
        className="flex h-24 items-center justify-center rounded bg-[#f3f4f6]"
        data-testid="audio-icon"
      >
        <svg
          className="h-10 w-10 text-[#9ca3af]"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M12 3v10.55A4 4 0 1014 17V7h4V3h-6z" />
        </svg>
      </div>

      {/* Description — prominent display */}
      {metadata.description && (
        <div>
          <div className="flex items-start gap-1">
            <p className="flex-1 text-sm text-[#374151]" data-testid="audio-description">
              {displayDesc}
            </p>
            <CopyButton text={metadata.description} label="Beschreibung kopieren" />
          </div>
          {descLong && (
            <button
              type="button"
              className="mt-1 text-xs text-[#1a56db] underline"
              onClick={() => setDescExpanded((p) => !p)}
              data-testid="description-toggle"
            >
              {descExpanded ? 'Weniger anzeigen' : 'Mehr anzeigen'}
            </button>
          )}
        </div>
      )}

      {/* Summary — one-sentence */}
      {metadata.summary && (
        <div className="flex items-start gap-1">
          <p className="flex-1 text-sm font-semibold text-[#1f2937]" data-testid="audio-summary">
            {metadata.summary}
          </p>
          <CopyButton text={metadata.summary} label="Zusammenfassung kopieren" />
        </div>
      )}

      {/* Keywords */}
      {metadata.keywords.length > 0 && (
        <div className="flex items-start gap-1">
          <div className="flex flex-1 flex-wrap gap-1.5" data-testid="audio-keywords">
            {metadata.keywords.map((kw) => (
              <Badge key={kw} variant="primary">
                {kw}
              </Badge>
            ))}
          </div>
          <CopyButton text={metadata.keywords.join(', ')} label="Schlüsselwörter kopieren" />
        </div>
      )}

      {/* Duration */}
      {metadata.duration_seconds !== null && (
        <p className="text-sm text-[#6b7280]" data-testid="audio-duration">
          Dauer: {formatDuration(metadata.duration_seconds)}
        </p>
      )}

      {/* Processing time */}
      <p className="text-xs text-[#9ca3af]" data-testid="processing-time">
        Verarbeitet in{' '}
        {metadata.processing_time_ms < 1000
          ? `${metadata.processing_time_ms} ms`
          : `${(metadata.processing_time_ms / 1000).toFixed(1)} s`}
      </p>
    </div>
  );
}
