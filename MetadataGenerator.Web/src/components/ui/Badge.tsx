/**
 * Badge / Chip component — small labeled element for keywords and tags.
 */
export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error';

export interface BadgeProps {
  /** Label text */
  children: string;
  /** Visual variant */
  variant?: BadgeVariant;
  /** Additional CSS classes */
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-[#f3f4f6] text-[#374151]',
  primary: 'bg-[#e8f0fe] text-[#123a95]',
  success: 'bg-green-50 text-green-700',
  warning: 'bg-amber-50 text-amber-700',
  error: 'bg-red-50 text-red-700',
};

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
