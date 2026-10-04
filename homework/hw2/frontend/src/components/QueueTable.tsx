import React, { useState } from 'react';
import type { Party } from '../types';
import { ArrowUpRight, X } from 'lucide-react';
import { StatusLabel } from './StatusLabel';
import { minutesSince } from '../lib/format';

interface QueueTableProps {
  parties: Party[];
  now: number;
  onNotify: (partyId: string) => Promise<void>;
  onOpenSeatModal: (party: Party) => void;
  onCancel: (partyId: string) => Promise<void>;
  onOpenGuestView: (partyId: string) => void;
  onAddParty: () => void;
}

type Filter = 'active' | 'seated' | 'cancelled' | 'all';

const isActive = (p: Party) => p.status === 'waiting' || p.status === 'notified';

const FILTERS: { id: Filter; label: string; match: (p: Party) => boolean }[] = [
  { id: 'active', label: 'In line', match: isActive },
  { id: 'seated', label: 'Seated', match: (p) => p.status === 'seated' },
  { id: 'cancelled', label: 'Removed', match: (p) => p.status === 'cancelled' || p.status === 'no_show' },
  { id: 'all', label: 'All', match: () => true },
];

export const QueueTable: React.FC<QueueTableProps> = ({
  parties,
  now,
  onNotify,
  onOpenSeatModal,
  onCancel,
  onOpenGuestView,
  onAddParty,
}) => {
  const [filter, setFilter] = useState<Filter>('active');

  const activeFilter = FILTERS.find((f) => f.id === filter)!;
  const rows = parties.filter(activeFilter.match);
  const queue = parties.filter(isActive);

  return (
    <section className="panel overflow-hidden" aria-labelledby="waitlist-heading">
      <div className="flex h-12 items-stretch justify-between border-b border-line px-5">
        <div className="flex items-stretch gap-6">
          <h2 id="waitlist-heading" className="flex items-center font-display text-[19px] leading-none">
            Waitlist
          </h2>
          <nav className="flex items-stretch gap-5" aria-label="Filter waitlist">
            {FILTERS.map((f) => {
              const selected = f.id === filter;
              return (
                <button
                  key={f.id}
                  onClick={() => setFilter(f.id)}
                  aria-pressed={selected}
                  className={`-mb-px flex items-center gap-1.5 border-b-2 text-[13px] transition-colors focus-visible:outline-none focus-visible:text-ink ${
                    selected
                      ? 'border-ink font-medium text-ink'
                      : 'border-transparent text-ink-2 hover:text-ink'
                  }`}
                >
                  {f.label}
                  <span className="num text-[12px] text-ink-3">{parties.filter(f.match).length}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="px-5 py-14 text-center">
          <p className="text-sm font-medium text-ink">
            {filter === 'active' ? 'Nobody is waiting' : 'No parties here yet'}
          </p>
          <p className="mt-1 text-[13px] text-ink-2">
            {filter === 'active'
              ? 'Walk-ins you add will appear here in arrival order.'
              : 'Parties move here as the service goes on.'}
          </p>
          {filter === 'active' && (
            <button onClick={onAddParty} className="btn btn-secondary mt-4">
              Add walk-in
            </button>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] border-collapse whitespace-nowrap text-left">
            <thead>
              <tr className="border-b border-line bg-subtle text-[12px] text-ink-3">
                <th className="h-9 w-12 pl-5 font-medium">#</th>
                <th className="font-medium">Guest</th>
                <th className="w-16 font-medium">Size</th>
                <th className="w-32 font-medium">Waiting</th>
                <th className="w-40 font-medium">Status</th>
                <th className="pr-5 text-right font-medium">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((party) => {
                const active = isActive(party);
                const position = active ? queue.findIndex((p) => p.id === party.id) + 1 : null;
                const waited = minutesSince(party.created_at, now);
                const overdue = active && waited > party.quoted_wait_min;
                const notifiedAgo =
                  party.status === 'notified' && party.notified_at
                    ? `${minutesSince(party.notified_at, now)} min ago`
                    : undefined;

                return (
                  <tr
                    key={party.id}
                    className="group border-b border-line last:border-b-0 transition-colors hover:bg-subtle"
                  >
                    <td className="num h-[60px] pl-5 text-[13px] text-ink-3">{position ?? '–'}</td>
                    <td className="py-2.5 pr-4">
                      <div className="text-sm font-medium text-ink whitespace-nowrap">{party.guest_name}</div>
                      <div className="mt-0.5 flex min-w-0 items-center gap-1.5 text-[12px] text-ink-3">
                        <span className="num whitespace-nowrap font-mono">{party.phone_number}</span>
                        {party.notes && (
                          <>
                            <span aria-hidden>·</span>
                            <span className="max-w-[260px] truncate text-ink-2" title={party.notes}>
                              {party.notes}
                            </span>
                          </>
                        )}
                      </div>
                    </td>
                    <td className="num text-sm text-ink">{party.party_size}</td>
                    <td>
                      {active ? (
                        <>
                          <div className={`num text-sm ${overdue ? 'font-medium text-danger' : 'text-ink'}`}>
                            {waited} min
                          </div>
                          <div className="num text-[12px] text-ink-3">quoted {party.quoted_wait_min}</div>
                        </>
                      ) : (
                        <div className="num text-[13px] text-ink-3">quoted {party.quoted_wait_min}</div>
                      )}
                    </td>
                    <td>
                      <StatusLabel status={party.status} detail={notifiedAgo} />
                    </td>
                    <td className="pr-5">
                      <div className="flex items-center justify-end gap-1.5">
                        {active && (
                          <>
                            <button
                              onClick={() => onNotify(party.id)}
                              className={`btn btn-secondary ${party.status === 'waiting' ? '' : 'invisible'}`}
                              tabIndex={party.status === 'waiting' ? 0 : -1}
                            >
                              Notify
                            </button>
                            <button onClick={() => onOpenSeatModal(party)} className="btn btn-dark">
                              Seat
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => onOpenGuestView(party.id)}
                          className="btn btn-ghost btn-icon"
                          title="Open guest view"
                          aria-label={`Open guest view for ${party.guest_name}`}
                        >
                          <ArrowUpRight className="size-4" strokeWidth={1.75} />
                        </button>
                        {active && (
                          <button
                            onClick={() => onCancel(party.id)}
                            className="btn btn-ghost btn-icon hover:bg-danger-soft hover:text-danger"
                            title="Remove from waitlist"
                            aria-label={`Remove ${party.guest_name} from waitlist`}
                          >
                            <X className="size-4" strokeWidth={1.75} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
