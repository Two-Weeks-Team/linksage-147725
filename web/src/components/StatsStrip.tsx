"use client";

import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export default function StatsStrip() {
  const stats = [
    { label: 'AI Accuracy', value: '≈ 92%' },
    { label: 'Sub‑second Search', value: '0.8 s' },
    { label: 'SOC 2 Certified', value: '' },
    { label: 'Enterprise Users', value: '30 +' }
  ];

  return (
    <div className={`flex flex-wrap justify-center gap-6 py-4 bg-muted rounded-md ${inter.variable} font-sans`}>
      {stats.map((s) => (
        <div key={s.label} className="text-center">
          <p className="text-primary font-semibold text-lg">{s.value || '✔'}</p>
          <p className="text-sm text-foreground">{s.label}</p>
        </div>
      ))}
    </div>
  );
}