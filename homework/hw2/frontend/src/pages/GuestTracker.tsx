import React, { useState, useEffect } from 'react';
import type { Party } from '../types';
import { api } from '../services/api';
import { ArrowLeft } from 'lucide-react';
import { Wordmark } from '../components/Wordmark';
import { minutesSince, ordinal } from '../lib/format';

interface GuestTrackerProps {
  partyId: string;
  onBackToDashboard: () => void;
}

export const GuestTracker: React.FC<GuestTrackerProps> = ({ partyId, onBackToDashboard }) => {
  const [party, setParty] = useState<Party | null>(null);
  const [parties, setParties] = useState<Party[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [cancelled, setCancelled] = useState(false);

  const loadData = async () => {
    try {
      const [currentParty, allParties] = await Promise.all([
        api.getParty(partyId),
        api.getWaitlist(),
      ]);
      setParty(currentParty);
      setParties(allParties);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [partyId]);

  const handleLeaveLine = async () => {
    if (!party) return;
    if (!window.confirm('Are you sure you want to leave the waitlist? This will give up your spot in line.')) {
      return;
    }

    setCancelling(true);
    try {
      await api.cancelParty(party.id);
      setCancelled(true);
      await loadData();
    } finally {
      setCancelling(false);
    }
  };

  const shell = (children: React.ReactNode) => (
    <div className="min-h-dvh bg-canvas">
      <header className="border-b border-line-strong/70 bg-header">
        <div className="mx-auto flex h-14 max-w-md items-center justify-between px-5">
          <Wordmark />
          <button onClick={onBackToDashboard} className="btn btn-ghost -mr-2 text-[13px]">
            <ArrowLeft className="size-4" strokeWidth={1.75} />
            Host stand
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-md px-5 py-6">{children}</main>
    </div>
  );

  if (loading) {
    return shell(
      <div className="panel space-y-3 p-6" aria-busy="true" aria-label="Loading">
        <div className="h-3 w-24 rounded bg-line" />
        <div className="h-12 w-32 rounded bg-line" />
        <div className="h-3 w-40 rounded bg-line" />
      </div>
    );
  }

  if (!party) {
    return shell(
      <div className="panel p-6">
        <h1 className="text-lg font-semibold tracking-[-0.01em]">We couldn't find this spot</h1>
        <p className="mt-1 text-sm text-ink-2">
          The link may be out of date, or the party was removed. Please check with the host.
        </p>
      </div>
    );
  }

  const activeQueue = parties.filter((p) => p.status === 'waiting' || p.status === 'notified');
  const positionIndex = activeQueue.findIndex((p) => p.id === party.id);
  const position = positionIndex >= 0 ? positionIndex + 1 : null;
  const waited = minutesSince(party.created_at, Date.now());
  const isRemoved = party.status === 'cancelled' || party.status === 'no_show' || cancelled;
  const isInLine = party.status === 'waiting' || party.status === 'notified';

  return shell(
    <div className="space-y-4">
      <p className="text-[13px] text-ink-2">
        {party.guest_name} · party of <span className="num">{party.party_size}</span>
      </p>

      {party.status === 'notified' ? (
        <section className="rounded-md border border-notified/25 bg-notified-soft p-6">
          <h1 className="text-[26px] leading-tight font-semibold tracking-[-0.02em] text-notified">
            Your table is ready
          </h1>
          <p className="mt-2 text-sm text-ink-2">
            Please come to the host stand within 5 minutes and show this screen.
          </p>
        </section>
      ) : party.status === 'seated' ? (
        <section className="rounded-md border border-seated/25 bg-seated-soft p-6">
          <h1 className="text-[26px] leading-tight font-semibold tracking-[-0.02em] text-seated">
            You're seated
          </h1>
          <p className="mt-2 text-sm text-ink-2">Enjoy your meal.</p>
        </section>
      ) : isRemoved ? (
        <section className="panel p-6">
          <h1 className="text-[22px] leading-tight font-semibold tracking-[-0.02em]">
            You've left the waitlist
          </h1>
          <p className="mt-2 text-sm text-ink-2">If this was a mistake, speak to the host.</p>
        </section>
      ) : (
        <section className="panel">
          <div className="p-6">
            <p className="text-[13px] text-ink-2">Your place in line</p>
            <p className="mt-1 flex items-baseline gap-2">
              <span className="num text-[72px] leading-none font-semibold tracking-[-0.04em] text-ink">
                {position ? ordinal(position) : '–'}
              </span>
            </p>
            <p className="mt-3 text-sm text-ink-2">
              {position === 1
                ? "You're next. We'll text you when your table is ready."
                : position
                  ? `${position - 1} ${position - 1 === 1 ? 'party' : 'parties'} ahead of you.`
                  : "We'll text you when your table is ready."}
            </p>
          </div>
          <dl className="grid grid-cols-2 border-t border-line">
            <div className="px-6 py-4">
              <dt className="text-[12px] text-ink-3">Quoted wait</dt>
              <dd className="num mt-0.5 text-[15px] font-medium">{party.quoted_wait_min} min</dd>
            </div>
            <div className="border-l border-line px-6 py-4">
              <dt className="text-[12px] text-ink-3">Waiting so far</dt>
              <dd className="num mt-0.5 text-[15px] font-medium">{waited} min</dd>
            </div>
          </dl>
        </section>
      )}

      {isInLine && !cancelled && (
        <div className="pt-2">
          <button
            onClick={handleLeaveLine}
            disabled={cancelling}
            className="btn btn-secondary h-10 w-full hover:border-danger/40 hover:bg-danger-soft hover:text-danger"
          >
            {cancelling ? 'Leaving…' : 'Leave the waitlist'}
          </button>
          <p className="mt-2 text-center text-[12px] text-ink-3">
            This page updates on its own. Plans changed? Leaving frees your spot for the next guest.
          </p>
        </div>
      )}
    </div>
  );
};
