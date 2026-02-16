/**
 * Tests for design theme tokens.
 */
import { describe, it, expect } from 'vitest';
import { colors, typography, spacing, radii, shadows } from './theme';

describe('Theme tokens', () => {
  it('has primary color palette', () => {
    expect(colors.primary[500]).toBeDefined();
    expect(typeof colors.primary[500]).toBe('string');
  });

  it('has neutral palette', () => {
    expect(colors.neutral[0]).toBe('#ffffff');
    expect(colors.neutral[900]).toBeDefined();
  });

  it('has semantic colors', () => {
    expect(colors.success).toBeDefined();
    expect(colors.warning).toBeDefined();
    expect(colors.error).toBeDefined();
    expect(colors.info).toBeDefined();
  });

  it('has font families', () => {
    expect(typography.fontFamily.sans).toContain('Inter');
  });

  it('has spacing scale', () => {
    expect(spacing[4]).toBe('1rem');
  });

  it('has border radii', () => {
    expect(radii.md).toBeDefined();
  });

  it('has shadows', () => {
    expect(shadows.md).toBeDefined();
  });
});
