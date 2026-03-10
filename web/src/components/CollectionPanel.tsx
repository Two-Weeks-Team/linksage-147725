"use client";
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

interface Bookmark {
  bookmark_id: string;
  url: string;
  title: string;
  summary: string;
  tags: string[];
  created_at: string;
}

interface CollectionProps {
  bookmarks: Bookmark[];
}

export default function CollectionPanel({ bookmarks }: CollectionProps) {
  if (!bookmarks.length) {
    return (
      <section className="mt-8">
        <h3 className="text-xl font-medium mb-4">Recent Activity</h3>
        <p className="text-muted">Your recent bookmarks will appear here.</p>
      </section>
    );
  }

  return (
    <section className="mt-8" >
      <h3 className="text-xl font-medium mb-4">Recent Activity</h3>
      <ul className="space-y-4">
        {bookmarks.map((bk) => (
          <li key={bk.bookmark_id} className="bg-card p-4 rounded-lg shadow-sm hover:shadow-md transition-fade">
            <a href={bk.url} target="_blank" rel="noopener noreferrer" className="block font-medium text-primary hover:underline">
              {bk.title || bk.url}
            </a>
            <p className="text-sm text-muted mt-1 line-clamp-2">
              {bk.summary}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {bk.tags.map((tag) => (
                <span key={tag} className="bg-muted text-sm rounded-full px-2 py-0.5">
                  {tag}
                </span>
              ))}
            </div>
            <time className="block text-xs text-muted mt-2">
              {new Date(bk.created_at).toLocaleString()}
            </time>
          </li>
        ))}
      </ul>
    </section>
  );
}
