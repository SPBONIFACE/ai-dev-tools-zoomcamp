import type { Party, Table, NotificationLog, AnalyticsSummary, CreatePartyInput, PartyStatus } from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Initial Mock Seed Data
const SEED_PARTIES: Party[] = [
  {
    id: 'p-101',
    guest_name: 'Elena Rostova',
    party_size: 2,
    phone_number: '+1 (555) 014-2201',
    notes: 'Window booth preferred. Quiet table.',
    quoted_wait_min: 15,
    status: 'waiting',
    table_id: null,
    created_at: new Date(Date.now() - 22 * 60000).toISOString(),
  },
  {
    id: 'p-102',
    guest_name: 'Marcus Vance',
    party_size: 4,
    phone_number: '+1 (555) 018-8832',
    notes: 'Needs 1 high chair.',
    quoted_wait_min: 30,
    status: 'waiting',
    table_id: null,
    created_at: new Date(Date.now() - 14 * 60000).toISOString(),
  },
  {
    id: 'p-103',
    guest_name: 'Sarah Jenkins',
    party_size: 6,
    phone_number: '+1 (555) 019-9941',
    notes: 'Birthday celebration.',
    quoted_wait_min: 40,
    status: 'notified',
    table_id: null,
    created_at: new Date(Date.now() - 35 * 60000).toISOString(),
    notified_at: new Date(Date.now() - 2 * 60000).toISOString(),
  },
];

const SEED_TABLES: Table[] = [
  { id: 'T1', name: 'Table 1', capacity: 2, status: 'available', current_party_id: null },
  { id: 'T2', name: 'Table 2', capacity: 2, status: 'available', current_party_id: null },
  { id: 'T3', name: 'Table 3', capacity: 4, status: 'available', current_party_id: null },
  { id: 'T4', name: 'Table 4', capacity: 4, status: 'available', current_party_id: null },
  { id: 'T5', name: 'Table 5', capacity: 6, status: 'available', current_party_id: null },
  { id: 'T6', name: 'Table 6', capacity: 6, status: 'available', current_party_id: null },
];

const SEED_NOTIFICATIONS: NotificationLog[] = [
  {
    id: 'notif-1',
    party_id: 'p-103',
    phone_number: '+1 (555) 019-9941',
    message: 'TableHop: Your table is ready! Please report to the host stand within 5 minutes.',
    sent_at: new Date(Date.now() - 2 * 60000).toISOString(),
  },
];

// In-Memory / LocalStorage Mock State Store
class MockStore {
  parties: Party[];
  tables: Table[];
  notifications: NotificationLog[];

  constructor() {
    const savedParties = localStorage.getItem('tablehop_parties');
    const savedTables = localStorage.getItem('tablehop_tables');
    const savedNotifs = localStorage.getItem('tablehop_notifications');

    this.parties = savedParties ? JSON.parse(savedParties) : SEED_PARTIES;
    this.tables = savedTables ? JSON.parse(savedTables) : SEED_TABLES;
    this.notifications = savedNotifs ? JSON.parse(savedNotifs) : SEED_NOTIFICATIONS;
  }

  save() {
    localStorage.setItem('tablehop_parties', JSON.stringify(this.parties));
    localStorage.setItem('tablehop_tables', JSON.stringify(this.tables));
    localStorage.setItem('tablehop_notifications', JSON.stringify(this.notifications));
  }
}

const mockStore = new MockStore();

// Centralized API Client
export const api = {
  isMockMode: () => USE_MOCK,

  // --- WAITLIST ---
  async getWaitlist(): Promise<Party[]> {
    if (USE_MOCK) {
      return [...mockStore.parties];
    }
    const res = await fetch(`${API_BASE_URL}/api/waitlist`);
    if (!res.ok) throw new Error('Failed to fetch waitlist');
    return res.json();
  },

  async getParty(id: string): Promise<Party | null> {
    if (USE_MOCK) {
      return mockStore.parties.find((p) => p.id === id) || null;
    }
    const res = await fetch(`${API_BASE_URL}/api/waitlist/${id}`);
    if (!res.ok) return null;
    return res.json();
  },

  async addParty(input: CreatePartyInput): Promise<Party> {
    if (USE_MOCK) {
      const activeWaiting = mockStore.parties.filter(
        (p) => p.status === 'waiting' || p.status === 'notified'
      ).length;
      const autoWait = (activeWaiting + 1) * 10;

      const newParty: Party = {
        id: `p-${Date.now()}`,
        guest_name: input.guest_name,
        party_size: Number(input.party_size),
        phone_number: input.phone_number,
        notes: input.notes,
        quoted_wait_min: input.quoted_wait_min ?? autoWait,
        status: 'waiting',
        table_id: null,
        created_at: new Date().toISOString(),
      };

      mockStore.parties.push(newParty);
      mockStore.save();
      return newParty;
    }

    const res = await fetch(`${API_BASE_URL}/api/waitlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    if (!res.ok) throw new Error('Failed to create party');
    return res.json();
  },

  async updatePartyStatus(id: string, status: PartyStatus): Promise<Party> {
    if (USE_MOCK) {
      const party = mockStore.parties.find((p) => p.id === id);
      if (!party) throw new Error('Party not found');
      party.status = status;
      if (status === 'seated') {
        party.seated_at = new Date().toISOString();
      }
      mockStore.save();
      return { ...party };
    }

    const res = await fetch(`${API_BASE_URL}/api/waitlist/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update party status');
    return res.json();
  },

  async notifyParty(id: string): Promise<{ party: Party; notification: NotificationLog }> {
    if (USE_MOCK) {
      const party = mockStore.parties.find((p) => p.id === id);
      if (!party) throw new Error('Party not found');
      party.status = 'notified';
      party.notified_at = new Date().toISOString();

      const notif: NotificationLog = {
        id: `notif-${Date.now()}`,
        party_id: party.id,
        phone_number: party.phone_number,
        message: `TableHop: Table is ready for ${party.guest_name}! Please proceed to the host stand.`,
        sent_at: new Date().toISOString(),
      };

      mockStore.notifications.unshift(notif);
      mockStore.save();
      return { party: { ...party }, notification: notif };
    }

    const res = await fetch(`${API_BASE_URL}/api/waitlist/${id}/notify`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to notify party');
    return res.json();
  },

  async cancelParty(id: string): Promise<Party> {
    if (USE_MOCK) {
      const party = mockStore.parties.find((p) => p.id === id);
      if (!party) throw new Error('Party not found');
      party.status = 'cancelled';

      // If party was occupying a table, release it
      if (party.table_id) {
        const table = mockStore.tables.find((t) => t.id === party.table_id);
        if (table) {
          table.status = 'available';
          table.current_party_id = null;
        }
        party.table_id = null;
      }

      mockStore.save();
      return { ...party };
    }

    const res = await fetch(`${API_BASE_URL}/api/waitlist/${id}/cancel`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to cancel party');
    return res.json();
  },

  // --- TABLES ---
  async getTables(): Promise<Table[]> {
    if (USE_MOCK) {
      return [...mockStore.tables];
    }
    const res = await fetch(`${API_BASE_URL}/api/tables`);
    if (!res.ok) throw new Error('Failed to fetch tables');
    return res.json();
  },

  async seatParty(tableId: string, partyId: string): Promise<{ table: Table; party: Party }> {
    if (USE_MOCK) {
      const table = mockStore.tables.find((t) => t.id === tableId);
      const party = mockStore.parties.find((p) => p.id === partyId);
      if (!table) throw new Error('Table not found');
      if (!party) throw new Error('Party not found');

      table.status = 'occupied';
      table.current_party_id = party.id;

      party.status = 'seated';
      party.table_id = table.id;
      party.seated_at = new Date().toISOString();

      mockStore.save();
      return { table: { ...table }, party: { ...party } };
    }

    const res = await fetch(`${API_BASE_URL}/api/tables/${tableId}/seat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ party_id: partyId }),
    });
    if (!res.ok) throw new Error('Failed to seat party');
    return res.json();
  },

  async clearTable(tableId: string): Promise<Table> {
    if (USE_MOCK) {
      const table = mockStore.tables.find((t) => t.id === tableId);
      if (!table) throw new Error('Table not found');

      table.status = 'available';
      table.current_party_id = null;

      mockStore.save();
      return { ...table };
    }

    const res = await fetch(`${API_BASE_URL}/api/tables/${tableId}/clear`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to clear table');
    return res.json();
  },

  // --- NOTIFICATIONS ---
  async getNotifications(): Promise<NotificationLog[]> {
    if (USE_MOCK) {
      return [...mockStore.notifications];
    }
    const res = await fetch(`${API_BASE_URL}/api/notifications`);
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  // --- ANALYTICS ---
  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    if (USE_MOCK) {
      const activeWaiting = mockStore.parties.filter(
        (p) => p.status === 'waiting' || p.status === 'notified'
      );
      const seatedToday = mockStore.parties.filter((p) => p.status === 'seated').length;
      const avgWait =
        activeWaiting.length > 0
          ? Math.round(
              activeWaiting.reduce((acc, curr) => acc + curr.quoted_wait_min, 0) /
                activeWaiting.length
            )
          : 0;

      return {
        active_waiting: activeWaiting.length,
        avg_wait_min: avgWait,
        total_seated_today: seatedToday,
      };
    }

    const res = await fetch(`${API_BASE_URL}/api/analytics/summary`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  // Reset Mock Data Helper
  resetMockData() {
    mockStore.parties = JSON.parse(JSON.stringify(SEED_PARTIES));
    mockStore.tables = JSON.parse(JSON.stringify(SEED_TABLES));
    mockStore.notifications = JSON.parse(JSON.stringify(SEED_NOTIFICATIONS));
    mockStore.save();
  },
};
