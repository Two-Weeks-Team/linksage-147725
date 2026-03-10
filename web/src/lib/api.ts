async function throwApiError(res: Response, fallback: string): Promise<never> {
  const raw = await res.text();
  const parsed = raw ? safeParseJson(raw) : null;
  const message = parsed?.error?.message ?? parsed?.detail ?? parsed?.message ?? raw ?? fallback;
  throw new Error(message || fallback);
}

function safeParseJson(raw: string): any {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export interface BookmarkPayload {
  url: string;
  title?: string;
  tags?: string[];
  notes?: string;
}

export interface BookmarkResponse {
  bookmark_id: string;
  url: string;
  title: string;
  summary: string;
  tags: string[];
  created_at: string;
}

export async function createBookmark(payload: BookmarkPayload): Promise<BookmarkResponse> {
  const res = await fetch('/api/bookmarks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    await throwApiError(res, "Failed to create bookmark");
  }
  return res.json();
}

export async function summarize(text: string): Promise<{ summary: string }> {
  const res = await fetch('/api/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    await throwApiError(res, "Summarization failed");
  }
  return res.json();
}

export async function fetchRecentBookmarks(): Promise<BookmarkResponse[]> {
  const res = await fetch('/api/bookmarks?limit=5');
  if (!res.ok) {
    await throwApiError(res, "Failed to fetch recent bookmarks");
  }
  const data = await res.json();
  // Assuming backend returns an array under "results" for list endpoints
  return data.results ?? [];
}
