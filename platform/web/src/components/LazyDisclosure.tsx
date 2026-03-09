'use client';

import { useState, type ReactNode } from 'react';

type LazyDisclosureProps = {
  summary: ReactNode;
  children: ReactNode;
  className?: string;
  defaultOpen?: boolean;
  placeholder?: ReactNode;
};

export function LazyDisclosure({
  summary,
  children,
  className,
  defaultOpen = false,
  placeholder,
}: LazyDisclosureProps) {
  const [hasOpened, setHasOpened] = useState(defaultOpen);

  return (
    <details
      className={className}
      open={defaultOpen}
      onToggle={(event) => {
        if ((event.currentTarget as HTMLDetailsElement).open) {
          setHasOpened(true);
        }
      }}
    >
      <summary>{summary}</summary>
      {hasOpened ? children : placeholder ?? null}
    </details>
  );
}
