/**
 * Tests for Card component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('renders without errors', () => {
    render(<Card>Content</Card>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders header when provided', () => {
    render(<Card header="Title">Body</Card>);
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Body')).toBeInTheDocument();
  });

  it('renders footer when provided', () => {
    render(<Card footer="Footer text">Body</Card>);
    expect(screen.getByText('Footer text')).toBeInTheDocument();
  });

  it('renders with header, body, and footer', () => {
    render(
      <Card header="Header" footer="Footer">
        Body content
      </Card>,
    );
    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Body content')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('does not render header/footer sections when not provided', () => {
    const { container } = render(<Card>Just body</Card>);
    // Only 1 child div (body), no header/footer borders
    const borderedDivs = container.querySelectorAll('.border-b, .border-t');
    expect(borderedDivs.length).toBe(0);
  });
});
