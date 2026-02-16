/**
 * Tests for Header component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Header } from './Header';

describe('Header', () => {
  it('renders default title', () => {
    render(<Header />);
    expect(screen.getByText('Metadata Generator')).toBeInTheDocument();
  });

  it('renders PoC badge', () => {
    render(<Header />);
    expect(screen.getByText('PoC')).toBeInTheDocument();
  });

  it('renders custom title', () => {
    render(<Header title="Custom App" />);
    expect(screen.getByText('Custom App')).toBeInTheDocument();
  });

  it('renders actions when provided', () => {
    render(<Header actions={<button>Action</button>} />);
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });

  it('has semantic header element', () => {
    render(<Header />);
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });
});
