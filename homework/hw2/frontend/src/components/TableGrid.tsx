import React from 'react';
import type { Table, Party } from '../types';

interface TableGridProps {
  tables: Table[];
  parties: Party[];
  onClearTable: (tableId: string) => Promise<void>;
}

export const TableGrid: React.FC<TableGridProps> = ({ tables, parties, onClearTable }) => {
  const openCount = tables.filter((t) => t.status === 'available').length;

  return (
    <section className="panel overflow-hidden" aria-labelledby="floor-heading">
      <div className="flex h-12 items-center justify-between border-b border-line px-5">
        <h2 id="floor-heading" className="font-display text-[19px] leading-none">
          Floor
        </h2>
        <span className="num text-[13px] text-ink-2">
          {openCount} of {tables.length} open
        </span>
      </div>

      <ul>
        {tables.map((table) => {
          const open = table.status === 'available';
          const party = table.current_party_id
            ? parties.find((p) => p.id === table.current_party_id)
            : undefined;

          return (
            <li
              key={table.id}
              className="flex h-[60px] items-center gap-3 border-b border-line px-5 last:border-b-0"
            >
              <span
                className={`num grid size-9 shrink-0 place-items-center rounded-[5px] font-mono text-[12px] font-medium ${
                  open ? 'border border-line-strong text-ink-2' : 'bg-accent-soft text-accent'
                }`}
              >
                {table.id}
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-medium text-ink">
                  {open ? table.name : party?.guest_name ?? 'Seated party'}
                </div>
                <div className="num truncate text-[12px] text-ink-3">
                  {open
                    ? `${table.capacity} seats`
                    : `${table.name} · ${party ? `${party.party_size} of ${table.capacity}` : table.capacity} seats`}
                </div>
              </div>
              {open ? (
                <span className="inline-flex items-center gap-2 text-[13px] text-ink-2">
                  <span className="size-1.5 rounded-full bg-seated" aria-hidden />
                  Open
                </span>
              ) : (
                <button onClick={() => onClearTable(table.id)} className="btn btn-secondary">
                  Clear
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
};
