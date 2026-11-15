import { renderAtlasHome } from '@/lib/render-home';

export const metadata = {
  title: { absolute: 'Valley-K Small · a research atlas of first-passage times' },
  description:
    'When does the time a random walker needs to reach a target split into two peaks? Bilingual reports, talks and a book on first-passage times on lattices with shortcuts, by Xiaoxiao Zhouyi.',
};

export default function EnHomePage() {
  return renderAtlasHome('en', '/en');
}
