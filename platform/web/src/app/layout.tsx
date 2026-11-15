import 'katex/dist/katex.min.css';
import '@/app/globals.css';

const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').replace(/\/$/, '');

export const metadata = {
  title: {
    default: 'Valley-K Small · a research atlas of first-passage times',
    template: '%s · Valley-K Small',
  },
  description:
    'Bilingual reports, talks and a book on first-passage times of random walks on lattices with shortcuts, by Xiaoxiao Zhouyi.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href={`${BASE_PATH}/favicon.svg`} type="image/svg+xml" />
      </head>
      <body>{children}</body>
    </html>
  );
}
