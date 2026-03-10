"use client";
import { useState } from 'react';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

interface HeroProps {
  onAdd: (url: string) => Promise<void>;
}

export default function Hero({ onAdd }: HeroProps) {
  const [url, setUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setSubmitting(true);
    setError('');
    try {
      await onAdd(url);
      setUrl('');
    } catch (e: any) {
      setError(e.message || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className={`flex flex-col items-center py-12 ${inter.variable} font-sans`}>
      <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
        LinkSage
      </h1>
      <p className="text-lg md:text-xl text-muted mb-6 text-center max-w-2xl">
        Securely transform bookmarks into actionable insights with reliable AI and enterprise‑grade security.
      </p>
      <form onSubmit={handleSubmit} className="w-full max-w-xl flex gap-2">
        <input
          type="url"
          required
          placeholder="Paste a URL…"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 rounded-l-md border border-border p-3 focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          type="submit"
          disabled={submitting}
          className="bg-primary text-white rounded-r-md px-5 py-3 hover:bg-primary/90 transition-fade disabled:opacity-50"
        >
          {submitting ? 'Processing…' : 'Summarize'}
        </button>
      </form>
      {error && <p className="mt-2 text-sm text-warning">{error}</p>}
    </section>
  );
}
