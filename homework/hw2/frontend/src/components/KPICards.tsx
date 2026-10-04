import React from 'react';
import type { AnalyticsSummary } from '../types';

interface KPICardsProps {
  summary: AnalyticsSummary;
  tablesOpen: number;
  tablesTotal: number;
}

export const KPICards: React.FC<KPICardsProps> = ({ summary, tablesOpen, tablesTotal }) => {
  const stats = [
    { label: 'Parties waiting', value: summary.active_waiting, unit: null },
    { label: 'Average quoted wait', value: summary.avg_wait_min, unit: 'min' },
    { label: 'Tables open', value: tablesOpen, unit: `of ${tablesTotal}` },
    { label: 'Seated this service', value: summary.total_seated_today, unit: null },
  ];

  return (
    <dl className="panel grid grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => (
        <div
          key={stat.label}
          className={`px-5 pt-4 pb-5 ${i > 0 ? 'lg:border-l' : ''} ${i % 2 === 1 ? 'border-l' : ''} ${
            i > 1 ? 'border-t lg:border-t-0' : ''
          } border-line`}
        >
          <dt className="text-[13px] text-ink-2">{stat.label}</dt>
          <dd className="mt-2 flex items-baseline gap-1.5">
            <span className="num text-[36px] leading-none font-semibold tracking-[-0.03em] text-ink">
              {stat.value}
            </span>
            {stat.unit && <span className="num text-[13px] text-ink-3">{stat.unit}</span>}
          </dd>
        </div>
      ))}
    </dl>
  );
};
