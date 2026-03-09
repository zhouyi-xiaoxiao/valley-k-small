import 'katex/dist/katex.min.css';
import '@/app/globals.css';

const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').replace(/\/$/, '');

export const metadata = {
  title: 'valley-k-small web atlas',
  description: 'Interactive bilingual research atlas for valley-k-small',
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
