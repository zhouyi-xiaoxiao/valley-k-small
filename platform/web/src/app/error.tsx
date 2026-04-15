'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: '#f8f4ea',
        color: '#1a1f1d',
        fontFamily: '"Space Grotesk", sans-serif',
        padding: '2rem',
      }}
    >
      <div style={{ maxWidth: '42rem' }}>
        <h1 style={{ marginBottom: '0.75rem' }}>Something went wrong</h1>
        <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>
          {error.message || 'The page hit a client-side rendering error.'}
        </p>
        <button
          type="button"
          onClick={reset}
          style={{
            borderRadius: '999px',
            padding: '0.7rem 1rem',
            border: '1px solid #d8ccb3',
            background: '#fffdf8',
            cursor: 'pointer',
          }}
        >
          Try again
        </button>
      </div>
    </main>
  );
}
