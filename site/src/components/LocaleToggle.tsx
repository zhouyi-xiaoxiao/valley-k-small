'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

function toEn(pathname: string): string {
  if (pathname === '/cn') {
    return '/';
  }
  if (pathname.startsWith('/cn/')) {
    return pathname.slice(3);
  }
  if (pathname.startsWith('/en/')) {
    return pathname.slice(3);
  }
  if (pathname === '/en') {
    return '/';
  }
  return pathname;
}

function toCn(pathname: string): string {
  if (pathname === '/') {
    return '/cn';
  }
  if (pathname.startsWith('/en/')) {
    return `/cn${pathname.slice(3)}`;
  }
  if (pathname === '/en') {
    return '/cn';
  }
  if (pathname.startsWith('/cn')) {
    return pathname;
  }
  return `/cn${pathname}`;
}

export function LocaleToggle({ lang }: { lang: 'en' | 'cn' }) {
  const pathname = usePathname() || '/';
  const enPath = toEn(pathname);
  const cnPath = toCn(pathname);

  return (
    <div className="locale-toggle" aria-label="language-switcher">
      <Link className={lang === 'en' ? 'active' : ''} href={enPath}>
        EN
      </Link>
      <Link className={lang === 'cn' ? 'active' : ''} href={cnPath}>
        中文
      </Link>
    </div>
  );
}
