/**
 * Tests for the AudioTile component.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { AudioTile } from '@/components/AudioTile';
import type { AudioMetadataResponse } from '@/lib/types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeMetadata(overrides: Partial<AudioMetadataResponse> = {}): AudioMetadataResponse {
  return {
    file_name: 'track.mp3',
    file_size: 4096,
    mime_type: 'audio/mpeg',
    description: 'An upbeat pop track with catchy melody.',
    keywords: ['pop', 'upbeat', 'melody'],
    summary: 'Energetic pop song with electronic elements.',
    duration_seconds: 222,
    processing_time_ms: 800,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('AudioTile', () => {
  it('renders all metadata fields', () => {
    render(<AudioTile metadata={makeMetadata()} />);
    expect(screen.getByTestId('audio-description')).toHaveTextContent('An upbeat pop track');
    expect(screen.getByTestId('audio-summary')).toHaveTextContent('Energetic pop song');
    expect(screen.getByTestId('audio-keywords')).toBeInTheDocument();
  });

  it('renders audio icon placeholder', () => {
    render(<AudioTile metadata={makeMetadata()} />);
    expect(screen.getByTestId('audio-icon')).toBeInTheDocument();
  });

  it('renders keywords as Badge components', () => {
    render(<AudioTile metadata={makeMetadata()} />);
    expect(screen.getByText('pop')).toBeInTheDocument();
    expect(screen.getByText('upbeat')).toBeInTheDocument();
    expect(screen.getByText('melody')).toBeInTheDocument();
  });

  it('renders duration in human-readable format (m:ss)', () => {
    render(<AudioTile metadata={makeMetadata({ duration_seconds: 222 })} />);
    expect(screen.getByTestId('audio-duration')).toHaveTextContent('Dauer: 3:42');
  });

  it('renders short durations correctly', () => {
    render(<AudioTile metadata={makeMetadata({ duration_seconds: 65 })} />);
    expect(screen.getByTestId('audio-duration')).toHaveTextContent('Dauer: 1:05');
  });

  it('hides duration when null', () => {
    render(<AudioTile metadata={makeMetadata({ duration_seconds: null })} />);
    expect(screen.queryByTestId('audio-duration')).not.toBeInTheDocument();
  });

  it('displays processing time', () => {
    render(<AudioTile metadata={makeMetadata({ processing_time_ms: 800 })} />);
    expect(screen.getByTestId('processing-time')).toHaveTextContent('Verarbeitet in 800 ms');
  });

  it('truncates long descriptions and toggles expand', async () => {
    const longDesc = 'B'.repeat(250);
    render(<AudioTile metadata={makeMetadata({ description: longDesc })} />);

    const descEl = screen.getByTestId('audio-description');
    expect(descEl.textContent?.length).toBeLessThan(250);
    expect(screen.getByTestId('description-toggle')).toHaveTextContent('Mehr anzeigen');

    await userEvent.click(screen.getByTestId('description-toggle'));
    expect(screen.getByTestId('audio-description')).toHaveTextContent(longDesc);
    expect(screen.getByTestId('description-toggle')).toHaveTextContent('Weniger anzeigen');
  });

  it('handles missing optional fields gracefully', () => {
    render(
      <AudioTile
        metadata={makeMetadata({
          summary: '',
          keywords: [],
          duration_seconds: null,
          description: '',
        })}
      />,
    );
    expect(screen.queryByTestId('audio-summary')).not.toBeInTheDocument();
    expect(screen.queryByTestId('audio-keywords')).not.toBeInTheDocument();
    expect(screen.queryByTestId('audio-duration')).not.toBeInTheDocument();
    // Processing time always visible
    expect(screen.getByTestId('processing-time')).toBeInTheDocument();
  });
});
