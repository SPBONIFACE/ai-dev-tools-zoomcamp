import React from 'react';
import type { NotificationLog } from '../types';
import { Modal } from './Modal';
import { parseTimestamp } from '../lib/format';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: NotificationLog[];
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  isOpen,
  onClose,
  notifications,
}) => (
  <Modal
    isOpen={isOpen}
    onClose={onClose}
    variant="sheet"
    title="Messages"
    description="Simulated SMS sent to guests. No real texts are delivered."
  >
    <div className="flex-1 overflow-y-auto">
      {notifications.length === 0 ? (
        <div className="px-5 py-16 text-center">
          <p className="text-sm font-medium text-ink">No messages sent</p>
          <p className="mt-1 text-[13px] text-ink-2">Use Notify on a waiting party to text them.</p>
        </div>
      ) : (
        <ol>
          {notifications.map((notif) => (
            <li key={notif.id} className="border-b border-line px-5 py-4">
              <div className="flex items-baseline justify-between gap-3">
                <span className="num font-mono text-[13px] text-ink">{notif.phone_number}</span>
                <time className="num font-mono text-[12px] text-ink-3" dateTime={notif.sent_at}>
                  {parseTimestamp(notif.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </time>
              </div>
              <p className="mt-1.5 text-[13px] leading-relaxed text-ink-2">{notif.message}</p>
            </li>
          ))}
        </ol>
      )}
    </div>
  </Modal>
);
