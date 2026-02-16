/**
 * Button component — primary, secondary, and ghost variants.
 *
 * Uses design tokens from theme.ts via Tailwind utility classes.
 */
import { type ButtonHTMLAttributes, forwardRef } from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[#1a56db] text-white hover:bg-[#1648b8] focus-visible:ring-[#1a56db]/50 disabled:bg-[#9ca3af]',
  secondary:
    'border border-[#d1d5db] bg-white text-[#374151] hover:bg-[#f3f4f6] focus-visible:ring-[#1a56db]/30 disabled:text-[#9ca3af]',
  ghost:
    'bg-transparent text-[#374151] hover:bg-[#f3f4f6] focus-visible:ring-[#1a56db]/30 disabled:text-[#9ca3af]',
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', loading = false, disabled, children, className = '', ...rest }, ref) => {
    const isDisabled = disabled || loading;
    return (
      <button
        ref={ref}
        type="button"
        disabled={isDisabled}
        className={`inline-flex items-center justify-center gap-2 rounded-[0.375rem] px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`}
        aria-busy={loading || undefined}
        {...rest}
      >
        {loading && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
            data-testid="spinner"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  },
);

Button.displayName = 'Button';

export { Button };
