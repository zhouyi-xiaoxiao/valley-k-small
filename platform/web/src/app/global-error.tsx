'use client';

export default function GlobalError({ error }: { error: Error & { digest?: string } }) {
  return (
    <html lang="en">
      <body
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          margin: 0,
          background: '#f8f4ea',
          color: '#1a1f1d',
          fontFamily: '"Space Grotesk", sans-serif',
          padding: '2rem',
        }}
      >
        <div style={{ maxWidth: '42rem' }}>
          <h1 style={{ marginBottom: '0.75rem' }}>Application error</h1>
          <p style={{ lineHeight: 1.6 }}>
            {error.message || 'A global rendering error occurred.'}
          </p>
        </div>
      </body>
    </html>
  );
}
