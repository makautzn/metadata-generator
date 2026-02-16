/**
 * ImageTile — renders image metadata fields inside a tile card.
 *
 * Shows thumbnail, description, keywords (as badges), caption,
 * and a collapsible EXIF section.
 */
'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui';
import { CopyButton } from '@/components/CopyButton';
import type { ImageMetadataResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface ImageTileProps {
  metadata: ImageMetadataResponse;
  thumbnailUrl: string | null;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DESCRIPTION_TRUNCATE_LENGTH = 200;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ImageTile({ metadata, thumbnailUrl }: ImageTileProps) {
  const [exifOpen, setExifOpen] = useState(false);
  const [descExpanded, setDescExpanded] = useState(false);

  const descLong = metadata.description.length > DESCRIPTION_TRUNCATE_LENGTH;
  const displayDesc =
    descLong && !descExpanded
      ? metadata.description.slice(0, DESCRIPTION_TRUNCATE_LENGTH) + '…'
      : metadata.description;

  const exifEntries = Object.entries(metadata.exif ?? {}).filter(([, v]) => v !== null && v !== '');
  const hasExif = exifEntries.length > 0;

  return (
    <div className="space-y-3" data-testid="image-tile">
      {/* Thumbnail */}
      {thumbnailUrl && (
        /* eslint-disable-next-line @next/next/no-img-element -- blob URL from local file, no Next.js Image optimization needed */
        <img
          src={thumbnailUrl}
          alt={metadata.caption || metadata.file_name}
          className="h-40 w-full rounded object-cover"
          data-testid="image-thumbnail"
        />
      )}

      {/* Description */}
      {metadata.description && (
        <div>
          <div className="flex items-start gap-1">
            <p className="flex-1 text-sm text-[#374151]" data-testid="image-description">
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

      {/* Caption */}
      {metadata.caption && (
        <div className="flex items-start gap-1">
          <blockquote
            className="flex-1 border-l-2 border-[#d1d5db] pl-3 text-sm italic text-[#6b7280]"
            data-testid="image-caption"
          >
            {metadata.caption}
          </blockquote>
          <CopyButton text={metadata.caption} label="Bildunterschrift kopieren" />
        </div>
      )}

      {/* Keywords */}
      {metadata.keywords.length > 0 && (
        <div className="flex items-start gap-1">
          <div className="flex flex-1 flex-wrap gap-1.5" data-testid="image-keywords">
            {metadata.keywords.map((kw) => (
              <Badge key={kw} variant="primary">
                {kw}
              </Badge>
            ))}
          </div>
          <CopyButton text={metadata.keywords.join(', ')} label="Schlüsselwörter kopieren" />
        </div>
      )}

      {/* EXIF section — collapsible */}
      {hasExif && (
        <div data-testid="exif-section">
          <button
            type="button"
            className="flex items-center gap-1 text-xs font-medium text-[#6b7280] hover:text-[#374151]"
            onClick={() => setExifOpen((p) => !p)}
            data-testid="exif-toggle"
          >
            <span>{exifOpen ? '▾' : '▸'}</span>
            EXIF-Daten
          </button>
          {exifOpen && (
            <dl
              className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs"
              data-testid="exif-data"
            >
              {exifEntries.map(([key, value]) => (
                <div key={key} className="contents">
                  <dt className="font-medium text-[#6b7280]">{key}</dt>
                  <dd className="text-[#374151]">{String(value)}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
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
