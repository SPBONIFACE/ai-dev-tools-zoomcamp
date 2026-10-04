import React, { useState, useEffect } from 'react';
import type { Party, Table, NotificationLog, AnalyticsSummary, CreatePartyInput } from '../types';
import { api } from '../services/api';
import { KPICards } from '../components/KPICards';
import { QueueTable } from '../components/QueueTable';
import { TableGrid } from '../components/TableGrid';
import { AddPartyModal } from '../components/AddPartyModal';
import { SeatModal } from '../components/SeatModal';
import { NotificationDrawer } from '../components/NotificationDrawer';
import { Wordmark } from '../components/Wordmark';
import { Plus, RotateCcw } from 'lucide-react';

interface HostDashboardProps {
  onOpenGuestView: (partyId: string) => void;
}

export const HostDashboard: React.FC<HostDashboardProps> = ({ onOpenGuestView }) => {
  const [parties, setParties] = useState<Party[]>([]);
  const [tables, setTables] = useState<Table[]>([]);
  const [notifications, setNotifications] = useState<NotificationLog[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary>({
    active_waiting: 0,
    avg_wait_min: 0,
    total_seated_today: 0,
  });
  const [loadError, setLoadError] = useState(false);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [seatModalParty, setSeatModalParty] = useState<Party | null>(null);
  const [isNotifDrawerOpen, setIsNotifDrawerOpen] = useState(false);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const refreshAll = async () => {
    try {
      const [waitlistData, tablesData, notifData, analyticsData] = await Promise.all([
        api.getWaitlist(),
        api.getTables(),
        api.getNotifications(),
        api.getAnalyticsSummary(),
      ]);
      setParties(waitlistData);
      setTables(tablesData);
      setNotifications(notifData);
      setAnalytics(analyticsData);
      setLoadError(false);
    } catch (err) {
      console.error('Failed to load data:', err);
      setLoadError(true);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const handleAddParty = async (data: CreatePartyInput) => {
    await api.addParty(data);
    await refreshAll();
  };

  const handleNotifyParty = async (partyId: string) => {
    await api.notifyParty(partyId);
    await refreshAll();
  };

  const handleSeatParty = async (tableId: string, partyId: string) => {
    await api.seatParty(tableId, partyId);
    await refreshAll();
  };

  const handleClearTable = async (tableId: string) => {
    await api.clearTable(tableId);
    await refreshAll();
  };

  const handleCancelParty = async (partyId: string) => {
    await api.cancelParty(partyId);
    await refreshAll();
  };

  const handleResetData = () => {
    if (window.confirm('Reset all waitlist and table data to default demo state?')) {
      api.resetMockData();
      refreshAll();
    }
  };

  const clock = new Date(now);
  const tablesOpen = tables.filter((t) => t.status === 'available').length;

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-30 border-b border-line-strong/70 bg-header">
        <div className="mx-auto flex h-14 max-w-[1320px] items-center justify-between gap-4 px-6">
          <div className="flex items-center gap-4">
            <Wordmark />
            <span className="h-4 w-px bg-line-strong" aria-hidden />
            <span className="text-[13px] text-ink-2">Host stand</span>
            {api.isMockMode() && (
              <span className="hidden rounded-[4px] border border-line px-1.5 py-0.5 text-[11px] font-medium text-ink-2 sm:inline">
                Demo data
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5">
            <time className="num mr-2 hidden font-mono text-[13px] text-ink-2 sm:block" dateTime={clock.toISOString()}>
              {clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </time>
            <button onClick={() => setIsNotifDrawerOpen(true)} className="btn btn-ghost">
              Messages
              {notifications.length > 0 && (
                <span className="num min-w-5 rounded-[4px] bg-ink px-1 text-center text-[11px] leading-5 font-medium text-white">
                  {notifications.length}
                </span>
              )}
            </button>
            {api.isMockMode() && (
              <button
                onClick={handleResetData}
                className="btn btn-ghost btn-icon"
                title="Reset demo data"
                aria-label="Reset demo data"
              >
                <RotateCcw className="size-4" strokeWidth={1.75} />
              </button>
            )}
            <button onClick={() => setIsAddModalOpen(true)} className="btn btn-primary ml-1.5">
              <Plus className="size-4" strokeWidth={2} />
              Add walk-in
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-[1320px] flex-1 px-6 pt-7 pb-10">
        <div className="mb-5 flex flex-wrap items-end justify-between gap-2">
          <div>
            <h1 className="font-display text-[30px] leading-tight tracking-[-0.01em]">Tonight's service</h1>
            <p className="mt-1 text-[13px] text-ink-2">
              {clock.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' })}
            </p>
          </div>
        </div>

        {loadError && (
          <div
            role="alert"
            className="mb-5 flex items-center justify-between gap-4 rounded-md border border-danger/25 bg-danger-soft px-4 py-3 text-[13px] text-danger"
          >
            <span>Couldn't reach the TableHop server. Check that the backend is running.</span>
            <button onClick={refreshAll} className="btn btn-secondary">
              Retry
            </button>
          </div>
        )}

        <KPICards summary={analytics} tablesOpen={tablesOpen} tablesTotal={tables.length} />

        <div className="mt-6 grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <QueueTable
            parties={parties}
            now={now}
            onNotify={handleNotifyParty}
            onOpenSeatModal={(party) => setSeatModalParty(party)}
            onCancel={handleCancelParty}
            onOpenGuestView={onOpenGuestView}
            onAddParty={() => setIsAddModalOpen(true)}
          />
          <TableGrid tables={tables} parties={parties} onClearTable={handleClearTable} />
        </div>
      </main>

      <AddPartyModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddParty}
        activeWaitingCount={analytics.active_waiting}
      />

      <SeatModal
        isOpen={!!seatModalParty}
        party={seatModalParty}
        tables={tables}
        onClose={() => setSeatModalParty(null)}
        onConfirmSeat={handleSeatParty}
      />

      <NotificationDrawer
        isOpen={isNotifDrawerOpen}
        onClose={() => setIsNotifDrawerOpen(false)}
        notifications={notifications}
      />
    </div>
  );
};
