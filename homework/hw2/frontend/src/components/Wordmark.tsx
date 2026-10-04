import React from 'react';

export const Wordmark: React.FC<{ size?: 'md' | 'lg' }> = ({ size = 'md' }) => {
  const mark = size === 'lg' ? 26 : 22;
  return (
    <span className="inline-flex items-center gap-2" aria-label="TableHop">
      {/* A round table seen from above, with four chairs. */}
      <svg width={mark} height={mark} viewBox="0 0 24 24" aria-hidden>
        <circle cx="12" cy="12" r="6" fill="var(--color-accent)" />
        <rect x="8" y="0.5" width="8" height="3.5" rx="1.75" fill="var(--color-ink)" />
        <rect x="8" y="20" width="8" height="3.5" rx="1.75" fill="var(--color-ink)" />
        <rect x="0.5" y="8" width="3.5" height="8" rx="1.75" fill="var(--color-ink)" />
        <rect x="20" y="8" width="3.5" height="8" rx="1.75" fill="var(--color-ink)" />
      </svg>
      <span
        className={`font-display leading-none tracking-[-0.01em] text-ink ${
          size === 'lg' ? 'text-[22px]' : 'text-[19px]'
        }`}
      >
        Table<span className="text-accent">Hop</span>
      </span>
    </span>
  );
};
