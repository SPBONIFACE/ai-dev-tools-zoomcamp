export type PartyStatus = 'waiting' | 'notified' | 'seated' | 'cancelled' | 'no_show';

export interface Party {
  id: string;
  guest_name: string;
  party_size: number;
  phone_number: string;
  notes?: string;
  quoted_wait_min: number;
  status: PartyStatus;
  table_id?: string | null;
  created_at: string;
  notified_at?: string | null;
  seated_at?: string | null;
}

export type TableStatus = 'available' | 'occupied';

export interface Table {
  id: string;
  name: string;
  capacity: number;
  status: TableStatus;
  current_party_id?: string | null;
}

export interface NotificationLog {
  id: string;
  party_id: string;
  phone_number: string;
  message: string;
  sent_at: string;
}

export interface AnalyticsSummary {
  active_waiting: number;
  avg_wait_min: number;
  total_seated_today: number;
}

export interface CreatePartyInput {
  guest_name: string;
  party_size: number;
  phone_number: string;
  notes?: string;
  quoted_wait_min?: number;
}
