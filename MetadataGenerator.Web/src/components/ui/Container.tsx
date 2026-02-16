/**
 * Container component — max-width centered layout wrapper.
 */
import type { ReactNode } from 'react';

export interface ContainerProps {
  /** Content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export function Container({ children, className = '' }: ContainerProps) {
  return <div className={`mx-auto w-full max-w-6xl px-4 sm:px-6 ${className}`}>{children}</div>;
}
