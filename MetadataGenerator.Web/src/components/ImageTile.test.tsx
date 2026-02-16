/**
 * Tests for the ImageTile component.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { ImageTile } from '@/components/ImageTile';
import type { ImageMetadataResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeMetadata(overrides: Partial<ImageMetadataResponse> = {}): ImageMetadataResponse {
  return {
    file_name: 'photo.jpg',
    file_size: 2048,
    mime_type: 'image/jpeg',
    description: 'A beautiful sunset over the mountains.',
    keywords: ['sunset', 'mountains', 'landscape'],
    caption: 'Golden hour in the Alps',
    exif: { Camera: 'Canon EOS R5', Date: '2024-06-15' },
    processing_time_ms: 450,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ImageTile', () => {
  it('renders all metadata fields', () => {
    render(<ImageTile metadata={makeMetadata()} thumbnailUrl={null} />);
    expect(screen.getByTestId('image-description')).toHaveTextContent('A beautiful sunset');
    expect(screen.getByTestId('image-caption')).toHaveTextContent('Golden hour in the Alps');
    expect(screen.getByTestId('image-keywords')).toBeInTheDocument();
  });

  it('renders thumbnail when URL is provided', () => {
    render(<ImageTile metadata={makeMetadata()} thumbnailUrl="blob:http://test/abc" />);
    const img = screen.getByTestId('image-thumbnail') as HTMLImageElement;
    expect(img.src).toBe('blob:http://test/abc');
  });

  it('does not render thumbnail when URL is null', () => {
    render(<ImageTile metadata={makeMetadata()} thumbnailUrl={null} />);
    expect(screen.queryByTestId('image-thumbnail')).not.toBeInTheDocument();
  });

  it('renders keywords as Badge components', () => {
    render(<ImageTile metadata={makeMetadata()} thumbnailUrl={null} />);
    expect(screen.getByText('sunset')).toBeInTheDocument();
    expect(screen.getByText('mountains')).toBeInTheDocument();
    expect(screen.getByText('landscape')).toBeInTheDocument();
  });

  it('renders EXIF data when present', async () => {
    render(<ImageTile metadata={makeMetadata()} thumbnailUrl={null} />);
    expect(screen.getByTestId('exif-section')).toBeInTheDocument();
    // EXIF is collapsed by default
    expect(screen.queryByTestId('exif-data')).not.toBeInTheDocument();

    // Expand EXIF
    await userEvent.click(screen.getByTestId('exif-toggle'));
    expect(screen.getByTestId('exif-data')).toBeInTheDocument();
    expect(screen.getByText('Camera')).toBeInTheDocument();
    expect(screen.getByText('Canon EOS R5')).toBeInTheDocument();
  });

  it('hides EXIF section when EXIF is empty', () => {
    render(<ImageTile metadata={makeMetadata({ exif: {} })} thumbnailUrl={null} />);
    expect(screen.queryByTestId('exif-section')).not.toBeInTheDocument();
  });

  it('hides EXIF section when all EXIF values are null', () => {
    render(
      <ImageTile
        metadata={makeMetadata({ exif: { Camera: null, Date: null } })}
        thumbnailUrl={null}
      />,
    );
    expect(screen.queryByTestId('exif-section')).not.toBeInTheDocument();
  });

  it('displays processing time in ms', () => {
    render(<ImageTile metadata={makeMetadata({ processing_time_ms: 320 })} thumbnailUrl={null} />);
    expect(screen.getByTestId('processing-time')).toHaveTextContent('Verarbeitet in 320 ms');
  });

  it('displays processing time in seconds for large values', () => {
    render(<ImageTile metadata={makeMetadata({ processing_time_ms: 2500 })} thumbnailUrl={null} />);
    expect(screen.getByTestId('processing-time')).toHaveTextContent('Verarbeitet in 2.5 s');
  });

  it('truncates long descriptions and toggles expand', async () => {
    const longDesc = 'A'.repeat(250);
    render(<ImageTile metadata={makeMetadata({ description: longDesc })} thumbnailUrl={null} />);

    // Should be truncated
    const descEl = screen.getByTestId('image-description');
    expect(descEl.textContent?.length).toBeLessThan(250);
    expect(screen.getByTestId('description-toggle')).toHaveTextContent('Mehr anzeigen');

    // Expand
    await userEvent.click(screen.getByTestId('description-toggle'));
    expect(screen.getByTestId('image-description')).toHaveTextContent(longDesc);
    expect(screen.getByTestId('description-toggle')).toHaveTextContent('Weniger anzeigen');
  });

  it('handles missing optional fields gracefully', () => {
    render(
      <ImageTile
        metadata={makeMetadata({
          caption: '',
          keywords: [],
          exif: {},
          description: '',
        })}
        thumbnailUrl={null}
      />,
    );
    expect(screen.queryByTestId('image-caption')).not.toBeInTheDocument();
    expect(screen.queryByTestId('image-keywords')).not.toBeInTheDocument();
    expect(screen.queryByTestId('exif-section')).not.toBeInTheDocument();
    // Processing time should still be visible
    expect(screen.getByTestId('processing-time')).toBeInTheDocument();
  });
});
