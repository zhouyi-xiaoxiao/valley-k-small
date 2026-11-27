import Link from 'next/link';
import { LocaleToggle } from '@/components/LocaleToggle';
import { OWNER_SITE, OWNER_SITE_ZH, formatDay, readerText } from '@/lib/atlas';
import { loadIndex, localizedText, prefixPath } from '@/lib/content';
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
  const generated = formatDay(lang, loadIndex().generated_at);
  return (
    <div className="atlas-root" lang={lang === 'cn' ? 'zh-CN' : 'en'}>
      <header className="shell">
        <div className="shell-inner">
          <Link className="brand" href={prefixPath(prefix, '/')}>
            <span className="brand-name">Valley-K Small</span>
            <span className="brand-sub">{localizedText(lang, 'research atlas', '研究图谱')}</span>
          </Link>
          <nav className="nav" aria-label={localizedText(lang, 'Main', '主导航')}>
            <Link href={prefixPath(prefix, '/reports')}>{localizedText(lang, 'Reports', '报告')}</Link>
            <Link href={`${prefixPath(prefix, '/')}#talks`}>{localizedText(lang, 'Talks', '演讲')}</Link>
            <Link href={prefixPath(prefix, '/book')}>{localizedText(lang, 'Book', '书')}</Link>
            <Link href={prefixPath(prefix, '/theory')}>{localizedText(lang, 'Theory', '理论')}</Link>
            <Link href={prefixPath(prefix, '/about')}>{localizedText(lang, 'About', '关于')}</Link>
          </nav>
          <LocaleToggle lang={lang} />
        </div>
      </header>
      <main>{children}</main>
      <footer className="atlas-footer">
        <div className="atlas-footer-inner">
          <a href={lang === 'cn' ? OWNER_SITE_ZH : OWNER_SITE}>
            {localizedText(lang, 'Xiaoxiao Zhouyi', '周易潇潇')} · zhouyixiaoxiao.com
          </a>
          <span>
            {generated
              ? readerText(localizedText(lang, `Pages generated from the reports on ${generated}`, `页面根据报告生成于 ${generated}`))
              : null}
            {' · '}
            <Link href={prefixPath(prefix, '/about')}>{localizedText(lang, 'About this atlas', '关于本图谱')}</Link>
          </span>
        </div>
      </footer>
    </div>
  );
}
