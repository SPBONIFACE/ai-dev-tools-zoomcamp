import React, { useState, useEffect } from 'react';
import type { CreatePartyInput } from '../types';
import { Modal, ModalFooter } from './Modal';

interface AddPartyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePartyInput) => Promise<void>;
  activeWaitingCount: number;
}

export const AddPartyModal: React.FC<AddPartyModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  activeWaitingCount,
}) => {
  const suggestedWait = (activeWaitingCount + 1) * 10;

  const [name, setName] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [phone, setPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [manualOverride, setManualOverride] = useState(false);
  const [waitMin, setWaitMin] = useState(suggestedWait);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!manualOverride) {
      setWaitMin(suggestedWait);
    }
  }, [suggestedWait, manualOverride]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !phone.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        guest_name: name.trim(),
        party_size: Number(partySize),
        phone_number: phone.trim(),
        notes: notes.trim() || undefined,
        quoted_wait_min: manualOverride ? Number(waitMin) : suggestedWait,
      });
      setName('');
      setPartySize(2);
      setPhone('');
      setNotes('');
      setManualOverride(false);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add walk-in" description="Adds the party to the end of the line.">
      <form onSubmit={handleSubmit}>
        <div className="space-y-4 px-5 py-5">
          <div>
            <label htmlFor="guest-name" className="field-label">
              Guest name
            </label>
            <input
              id="guest-name"
              type="text"
              required
              autoFocus
              autoComplete="off"
              placeholder="Eleanor Vance"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="field-input"
            />
          </div>

          <div className="grid grid-cols-[96px_1fr] gap-3">
            <div>
              <label htmlFor="party-size" className="field-label">
                Party size
              </label>
              <input
                id="party-size"
                type="number"
                min="1"
                max="12"
                required
                value={partySize}
                onChange={(e) => setPartySize(Math.max(1, parseInt(e.target.value) || 1))}
                className="field-input num"
              />
            </div>
            <div>
              <label htmlFor="phone" className="field-label">
                Mobile number
              </label>
              <input
                id="phone"
                type="tel"
                required
                autoComplete="off"
                placeholder="+1 (312) 847-1928"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="field-input num font-mono text-[13px]"
              />
            </div>
          </div>

          <div>
            <label htmlFor="notes" className="field-label">
              Notes <span className="font-normal text-ink-3">optional</span>
            </label>
            <input
              id="notes"
              type="text"
              placeholder="High chair, booth, birthday"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="field-input"
            />
          </div>

          <div className="flex items-center justify-between gap-4 rounded-md border border-line bg-subtle px-3.5 py-3">
            <div>
              <div className="text-[13px] font-medium text-ink">Quoted wait</div>
              <div className="text-[12px] text-ink-3">
                {manualOverride
                  ? 'Set by host'
                  : `10 min per party in line, including this one`}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {manualOverride ? (
                <div className="flex items-center gap-1.5">
                  <input
                    type="number"
                    min="0"
                    max="180"
                    aria-label="Quoted wait in minutes"
                    value={waitMin}
                    onChange={(e) => setWaitMin(Math.max(0, parseInt(e.target.value) || 0))}
                    className="field-input num h-8 w-16 px-2 text-right"
                  />
                  <span className="text-[13px] text-ink-2">min</span>
                </div>
              ) : (
                <span className="num text-[15px] font-semibold text-ink">{suggestedWait} min</span>
              )}
              <button
                type="button"
                onClick={() => setManualOverride((v) => !v)}
                className="btn btn-ghost h-7 px-2 text-[12px]"
              >
                {manualOverride ? 'Use suggested' : 'Adjust'}
              </button>
            </div>
          </div>
        </div>

        <ModalFooter>
          <button type="button" onClick={onClose} className="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={isSubmitting} className="btn btn-primary">
            {isSubmitting ? 'Adding…' : 'Add to waitlist'}
          </button>
        </ModalFooter>
      </form>
    </Modal>
  );
};
