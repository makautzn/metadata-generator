/**
 * Design tokens for the Metadata Generator UI.
 *
 * Inspired by DIE RHEINPFALZ editorial design — clean, authoritative,
 * with a focus on readability and content hierarchy.
 */

export const colors = {
  /** Primary brand — deep editorial blue */
  primary: {
    50: '#e8f0fe',
    100: '#c5d9fc',
    200: '#9fbefa',
    300: '#78a3f8',
    400: '#5a8ef5',
    500: '#1a56db',
    600: '#1648b8',
    700: '#123a95',
    800: '#0e2c72',
    900: '#0a1e4f',
  },

  /** Neutral greys for text, borders, backgrounds */
  neutral: {
    0: '#ffffff',
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  /** Accent — warm red similar to RHEINPFALZ masthead */
  accent: {
    500: '#c0392b',
    600: '#a93226',
    700: '#922b21',
  },

  /** Semantic colors */
  success: '#16a34a',
  warning: '#d97706',
  error: '#dc2626',
  info: '#2563eb',
} as const;

export const typography = {
  /** Font family — Inter for body, system fallback */
  fontFamily: {
    sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"Fira Code", "Cascadia Code", "JetBrains Mono", monospace',
  },

  /** Font sizes (rem) */
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },

  /** Font weights */
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;

export const spacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
} as const;

export const radii = {
  none: '0',
  sm: '0.25rem',
  md: '0.375rem',
  lg: '0.5rem',
  xl: '0.75rem',
  full: '9999px',
} as const;

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
} as const;
