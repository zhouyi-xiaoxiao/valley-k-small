import Link from 'next/link';
import { LocaleToggle } from '@/components/LocaleToggle';
import { localizedText, prefixPath } from '@/lib/content';
import type { Lang } from '@/types';

export function AppShell({
  lang,
  prefix,
  children,
}: {
  lang: Lang;
  prefix: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <header className="shell">
        <div className="shell-inner">
          <Link className="brand" href={prefixPath(prefix, '/')}>
            valley-k-small
          </Link>
          <nav className="nav">
            <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'Book', '书籍')}</Link>
            <Link href={prefixPath(prefix, '/reports')}>
              {localizedText(lang, 'Reports', '报告')}
            </Link>
            <Link href={prefixPath(prefix, '/theory')}>
              {localizedText(lang, 'Theory', '理论')}
            </Link>
            <Link href={prefixPath(prefix, '/agent-sync')}>Agent Sync</Link>
            <Link href={prefixPath(prefix, '/about')}>{localizedText(lang, 'About', '关于')}</Link>
            <LocaleToggle lang={lang} />
          </nav>
        </div>
      </header>
      <main>{children}</main>
    </>
  );
}
