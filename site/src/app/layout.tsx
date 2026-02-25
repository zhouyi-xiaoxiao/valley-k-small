import 'katex/dist/katex.min.css';
import '@/app/globals.css';

export const metadata = {
  title: 'valley-k-small web atlas',
  description: 'Interactive bilingual research atlas for valley-k-small',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
