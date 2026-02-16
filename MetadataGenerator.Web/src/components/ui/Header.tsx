/**
 * Header component — application header bar.
 */
import type { ReactNode } from 'react';

export interface HeaderProps {
  /** Application title */
  title?: string;
  /** Optional right-side actions */
  actions?: ReactNode;
}

export function Header({ title = 'Metadata Generator', actions }: HeaderProps) {
  return (
    <header className="border-b border-[#e5e7eb] bg-white px-6 py-4">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold tracking-tight text-[#1f2937]">{title}</h1>
          <span className="rounded-full bg-[#e8f0fe] px-2.5 py-0.5 text-xs font-medium text-[#123a95]">
            PoC
          </span>
        </div>
        {actions && <div>{actions}</div>}
      </div>
    </header>
  );
}
