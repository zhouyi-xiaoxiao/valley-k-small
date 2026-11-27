import { loadBookManifest } from '@/lib/content';
import { renderBookChapterPage } from '@/lib/render-book-pages';

export function generateStaticParams() {
  const manifest = loadBookManifest();
  return (manifest?.chapters || []).map((item) => ({ chapter: item.chapter_id }));
}

export function generateMetadata({ params }: { params: { chapter: string } }) {
  const chapter = (loadBookManifest()?.chapters || []).find((item) => item.chapter_id === params.chapter);
  return { title: chapter?.title_en || 'Book' };
}

export default function EnBookChapterPage({ params }: { params: { chapter: string } }) {
  return renderBookChapterPage('en', '/en', params.chapter);
}
