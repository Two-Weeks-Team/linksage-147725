import './globals.css';

export const metadata = {
  title: 'LinkSage – Secure AI Bookmark Manager',
  description: 'Securely transform bookmarks into actionable insights with reliable AI and enterprise‑grade security.'
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-background text-foreground antialiased">
      <body className="min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
