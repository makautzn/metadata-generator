/**
 * Card component — content container with optional header, body, and footer.
 *
 * Used as the tile wrapper for metadata results.
 */
import type { ReactNode } from 'react';

export interface CardProps {
  /** Optional header content */
  header?: ReactNode;
  /** Main body content */
  children: ReactNode;
  /** Optional footer content */
  footer?: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export function Card({ header, children, footer, className = '' }: CardProps) {
  return (
    <div
      className={`rounded-[0.5rem] border border-[#e5e7eb] bg-white shadow-[0_1px_2px_0_rgba(0,0,0,0.05)] ${className}`}
    >
      {header && (
        <div className="border-b border-[#e5e7eb] px-4 py-3 font-medium text-[#1f2937]">
          {header}
        </div>
      )}
      <div className="px-4 py-4">{children}</div>
      {footer && (
        <div className="border-t border-[#e5e7eb] px-4 py-3 text-sm text-[#6b7280]">{footer}</div>
      )}
    </div>
  );
}
