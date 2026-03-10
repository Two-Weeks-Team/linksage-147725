"use client";
import { useEffect, useState } from 'react';
import Hero from '@/components/Hero';
import InsightPanel from '@/components/InsightPanel';
import CollectionPanel from '@/components/CollectionPanel';
import StatsStrip from '@/components/StatsStrip';
import StatePanel from '@/components/StatePanel';
import { createBookmark, summarize, fetchRecentBookmarks } from '@/lib/api';

interface Bookmark {
  bookmark_id: string;
  url: string;
  title: string;
  summary: string;
  tags: string[];
  created_at: string;
}

export default function HomePage() {
  const [summary, setSummary] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [recent, setRecent] = useState<Bookmark[]>([]);

  const handleAdd = async (url: string) => {
    setLoading(true);
    setError('');
    try {
      // Step 1 – create bookmark (backend triggers AI summarization)
      const bk = await createBookmark({ url, title: '', tags: [], notes: '' });
      setSummary(bk.summary);
      // Refresh recent list
      const recentList = await fetchRecentBookmarks();
      setRecent(recentList);
    } catch (e: any) {
      setError(e.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  // Load recent activity on mount
  useEffect(() => {
    (async () => {
      try {
        const recentList = await fetchRecentBookmarks();
        setRecent(recentList);
      } catch (_) {}
    })();
  }, []);

  return (
    <main className="flex-1 container mx-auto px-4 py-8 space-y-12">
      <Hero onAdd={handleAdd} />
      <StatsStrip />
      <StatePanel status={loading ? 'loading' : error ? 'error' : ''} message={error} />
      {summary && <InsightPanel summary={summary} />}
      <CollectionPanel bookmarks={recent} />
    </main>
  );
}
