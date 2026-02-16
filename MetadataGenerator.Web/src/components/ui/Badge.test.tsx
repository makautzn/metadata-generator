/**
 * Tests for Badge component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders with text content', () => {
    render(<Badge>Keyword</Badge>);
    expect(screen.getByText('Keyword')).toBeInTheDocument();
  });

  it('uses default variant styling', () => {
    render(<Badge>Default</Badge>);
    const el = screen.getByText('Default');
    expect(el.className).toContain('bg-[#f3f4f6]');
  });

  it('renders primary variant', () => {
    render(<Badge variant="primary">Primary</Badge>);
    const el = screen.getByText('Primary');
    expect(el.className).toContain('bg-[#e8f0fe]');
  });

  it('renders success variant', () => {
    render(<Badge variant="success">OK</Badge>);
    expect(screen.getByText('OK').className).toContain('bg-green-50');
  });

  it('renders warning variant', () => {
    render(<Badge variant="warning">Warn</Badge>);
    expect(screen.getByText('Warn').className).toContain('bg-amber-50');
  });

  it('renders error variant', () => {
    render(<Badge variant="error">Err</Badge>);
    expect(screen.getByText('Err').className).toContain('bg-red-50');
  });

  it('applies additional className', () => {
    render(<Badge className="extra">Tag</Badge>);
    expect(screen.getByText('Tag').className).toContain('extra');
  });
});
