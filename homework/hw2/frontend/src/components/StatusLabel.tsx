import React from 'react';
import type { PartyStatus } from '../types';

const STATUS: Record<PartyStatus, { label: string; dot: string }> = {
  waiting: { label: 'Waiting', dot: 'bg-waiting' },
  notified: { label: 'Notified', dot: 'bg-notified' },
  seated: { label: 'Seated', dot: 'bg-seated' },
  cancelled: { label: 'Cancelled', dot: 'bg-ink-3' },
  no_show: { label: 'No-show', dot: 'bg-danger' },
};

export const StatusLabel: React.FC<{ status: PartyStatus; detail?: string }> = ({ status, detail }) => (
  <span className="inline-flex items-center gap-2 whitespace-nowrap text-[13px] text-ink">
    <span className={`size-1.5 rounded-full ${STATUS[status].dot}`} aria-hidden />
    {STATUS[status].label}
    {detail && <span className="text-ink-3 num">{detail}</span>}
  </span>
);
