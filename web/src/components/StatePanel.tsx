"use client";

interface StatePanelProps {
  status: 'loading' | 'error' | '';
  message?: string;
}

export default function StatePanel({ status, message }: StatePanelProps) {
  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="spinner" aria-label="Loading"></div>
      </div>
    );
  }
  if (status === 'error') {
    return (
      <div className="bg-warning/10 border border-warning text-warning rounded-md p-4 mt-4">
        <p>{message || 'An unexpected error occurred.'}</p>
      </div>
    );
  }
  return null;
}