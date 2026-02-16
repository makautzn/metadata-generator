/**
 * Tests for the CopyButton component.
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { CopyButton } from '@/components/CopyButton';

describe('CopyButton', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls navigator.clipboard.writeText with correct value', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<CopyButton text="Hello World" />);
    await userEvent.click(screen.getByTestId('copy-button'));

    expect(writeText).toHaveBeenCalledWith('Hello World');
  });

  it('shows Kopiert! feedback after successful copy', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<CopyButton text="test" />);
    await userEvent.click(screen.getByTestId('copy-button'));

    await waitFor(() => {
      expect(screen.getByTestId('copy-feedback')).toHaveTextContent('Kopiert!');
    });
  });

  it('copies keywords as comma-separated string', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<CopyButton text="sunset, mountains, landscape" />);
    await userEvent.click(screen.getByTestId('copy-button'));

    expect(writeText).toHaveBeenCalledWith('sunset, mountains, landscape');
  });

  it('falls back to execCommand when Clipboard API is unavailable', async () => {
    // Remove clipboard API
    Object.assign(navigator, { clipboard: undefined });
    const execCommand = vi.fn().mockReturnValue(true);
    document.execCommand = execCommand;

    render(<CopyButton text="fallback text" />);
    await userEvent.click(screen.getByTestId('copy-button'));

    expect(execCommand).toHaveBeenCalledWith('copy');
  });

  it('renders accessible label', () => {
    render(<CopyButton text="test" label="Beschreibung kopieren" />);
    expect(screen.getByLabelText('Beschreibung kopieren')).toBeInTheDocument();
  });
});
