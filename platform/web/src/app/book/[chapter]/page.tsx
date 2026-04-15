import { loadBookManifest } from '@/lib/content';
import { renderBookChapterPage } from '@/lib/render-book-pages';

export const dynamicParams = false;

export async function generateStaticParams() {
  const manifest = loadBookManifest();
  return (manifest?.chapters || []).map((item) => ({ chapter: item.chapter_id }));
}

export default function BookChapterPage({ params }: { params: { chapter: string } }) {
  return renderBookChapterPage('en', '', params.chapter);
}
