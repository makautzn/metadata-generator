/**
 * Tests for FileUpload component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FileUpload } from './FileUpload';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeFile(name: string, type: string, sizeKb = 10): File {
  const content = new Uint8Array(sizeKb * 1024);
  return new File([content], name, { type });
}

function makeFiles(specs: Array<{ name: string; type: string; sizeKb?: number }>): File[] {
  return specs.map((s) => makeFile(s.name, s.type, s.sizeKb));
}

function selectFiles(input: HTMLElement, fileList: File[]) {
  Object.defineProperty(input, 'files', { value: fileList, writable: false });
  fireEvent.change(input);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('FileUpload', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders drop zone with instructional text in German', () => {
    render(<FileUpload />);
    expect(
      screen.getByText(/Dateien hierher ziehen oder klicken zum Auswählen/),
    ).toBeInTheDocument();
  });

  it('updates file list when files are selected', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('photo.jpg', 'image/jpeg')]);
    expect(screen.getByText('photo.jpg')).toBeInTheDocument();
    expect(screen.getByText('1 Datei ausgewählt')).toBeInTheDocument();
  });

  it('shows plural label for multiple files', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(
      input,
      makeFiles([
        { name: 'a.jpg', type: 'image/jpeg' },
        { name: 'b.png', type: 'image/png' },
      ]),
    );
    expect(screen.getByText('2 Dateien ausgewählt')).toBeInTheDocument();
  });

  it('shows error when selecting more than 20 files', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    const many = Array.from({ length: 21 }, (_, i) => makeFile(`f${i}.jpg`, 'image/jpeg'));
    selectFiles(input, many);
    expect(screen.getByRole('alert')).toHaveTextContent(/Maximal 20 Dateien/);
  });

  it('flags unsupported file types with inline error', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('note.txt', 'text/plain')]);
    expect(screen.getByText(/Nicht unterstützter Dateityp/)).toBeInTheDocument();
  });

  it('flags oversized image with error', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('big.jpg', 'image/jpeg', 11_000)]);
    expect(screen.getByText(/zu groß/)).toBeInTheDocument();
  });

  it('removes a file when remove button is clicked', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('a.jpg', 'image/jpeg')]);
    expect(screen.getByText('a.jpg')).toBeInTheDocument();
    // Find remove button
    const removeBtn = screen.getByLabelText('a.jpg entfernen');
    fireEvent.click(removeBtn);
    expect(screen.queryByText('a.jpg')).not.toBeInTheDocument();
  });

  it('clears all files when "Alle entfernen" is clicked', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(
      input,
      makeFiles([
        { name: 'a.jpg', type: 'image/jpeg' },
        { name: 'b.wav', type: 'audio/wav' },
      ]),
    );
    expect(screen.getByText('2 Dateien ausgewählt')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('clear-all'));
    expect(screen.queryByText('a.jpg')).not.toBeInTheDocument();
  });

  it('disables Analyze button when no valid files', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('bad.txt', 'text/plain')]);
    const btn = screen.getByTestId('analyze-button');
    expect(btn).toBeDisabled();
  });

  it('enables Analyze button when valid files are selected', () => {
    render(<FileUpload />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('ok.jpg', 'image/jpeg')]);
    const btn = screen.getByTestId('analyze-button');
    expect(btn).not.toBeDisabled();
  });

  it('shows drag-over highlight on drop zone', () => {
    render(<FileUpload />);
    const zone = screen.getByTestId('drop-zone');
    fireEvent.dragOver(zone, { dataTransfer: { files: [] } });
    expect(zone.className).toContain('border-[#1a56db]');
  });

  it('removes highlight on drag leave', () => {
    render(<FileUpload />);
    const zone = screen.getByTestId('drop-zone');
    fireEvent.dragOver(zone, { dataTransfer: { files: [] } });
    fireEvent.dragLeave(zone, { dataTransfer: { files: [] } });
    expect(zone.className).not.toContain('border-[#1a56db]');
  });

  it('calls API client when Analyze button is clicked', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          results: [],
          total_files: 0,
          successful: 0,
          failed: 0,
          total_processing_time_ms: 0,
        }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const onResults = vi.fn();
    render(<FileUpload onResults={onResults} />);
    const input = screen.getByTestId('file-input');
    selectFiles(input, [makeFile('img.jpg', 'image/jpeg')]);
    fireEvent.click(screen.getByTestId('analyze-button'));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(onResults).toHaveBeenCalled();
    });
  });
});
