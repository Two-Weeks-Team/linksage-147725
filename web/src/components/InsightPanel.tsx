"use client";
import { Merriweather } from 'next/font/google';

const merri = Merriweather({ subsets: ['latin'], variable: '--font-merri' });

interface InsightProps {
  summary: string;
}

export default function InsightPanel({ summary }: InsightProps) {
  return (
    <section className={`mt-8 p-6 bg-card rounded-lg shadow ${merri.variable} font-serif`}>
      <h2 className="text-2xl font-semibold mb-4 text-primary">AI‑Generated Summary</h2>
      <p className="whitespace-pre-line text-foreground leading-relaxed">
        {summary}
      </p>
    </section>
  );
}
