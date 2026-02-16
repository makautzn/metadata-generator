/**
 * Tests for Container component.
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Container } from './Container';

describe('Container', () => {
  it('renders children', () => {
    render(<Container>Hello</Container>);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('has max-width constraint', () => {
    const { container } = render(<Container>Content</Container>);
    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.className).toContain('max-w-6xl');
  });

  it('applies additional className', () => {
    const { container } = render(<Container className="mt-8">Content</Container>);
    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.className).toContain('mt-8');
  });
});
