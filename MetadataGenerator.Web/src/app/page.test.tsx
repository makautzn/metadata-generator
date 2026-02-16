/**
 * Tests for the Home page component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Home from './page';

describe('Home page', () => {
  it('renders without errors', () => {
    render(<Home />);
    expect(screen.getByText('Metadata Generator')).toBeInTheDocument();
  });

  it('renders the header with PoC badge', () => {
    render(<Home />);
    expect(screen.getByText('PoC')).toBeInTheDocument();
  });

  it('renders the file upload drop zone', () => {
    render(<Home />);
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
  });

  it('renders the footer', () => {
    render(<Home />);
    const footer = screen.getByRole('contentinfo');
    expect(footer).toBeInTheDocument();
    expect(footer.textContent).toMatch(/Metadata Generator/);
  });
});
