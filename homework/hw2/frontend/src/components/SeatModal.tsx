import React, { useState } from 'react';
import type { Party, Table } from '../types';
import { Modal, ModalFooter } from './Modal';

interface SeatModalProps {
  isOpen: boolean;
  party: Party | null;
  tables: Table[];
  onClose: () => void;
  onConfirmSeat: (tableId: string, partyId: string) => Promise<void>;
}

export const SeatModal: React.FC<SeatModalProps> = ({
  isOpen,
  party,
  tables,
  onClose,
  onConfirmSeat,
}) => {
  const [selectedTableId, setSelectedTableId] = useState<string>('');
  const [isSeating, setIsSeating] = useState(false);

  if (!party) return null;

  const close = () => {
    setSelectedTableId('');
    onClose();
  };

  const availableTables = tables
    .filter((t) => t.status === 'available')
    .sort((a, b) => {
      const aFits = a.capacity >= party.party_size;
      const bFits = b.capacity >= party.party_size;
      if (aFits !== bFits) return aFits ? -1 : 1;
      return a.capacity - b.capacity;
    });

  const handleSeat = async () => {
    if (!selectedTableId) return;
    setIsSeating(true);
    try {
      await onConfirmSeat(selectedTableId, party.id);
      close();
    } finally {
      setIsSeating(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={close}
      title={`Seat ${party.guest_name}`}
      description={
        <>
          Party of {party.party_size}
          {party.notes && <span className="text-ink-3"> · {party.notes}</span>}
        </>
      }
    >
      <div className="px-5 py-5">
        {availableTables.length === 0 ? (
          <div className="rounded-md border border-line bg-subtle px-4 py-6 text-center">
            <p className="text-sm font-medium text-ink">No tables are open</p>
            <p className="mt-1 text-[13px] text-ink-2">Clear a table on the floor, then seat this party.</p>
          </div>
        ) : (
          <fieldset>
            <legend className="field-label">Choose a table</legend>
            <div className="max-h-72 divide-y divide-line overflow-y-auto rounded-md border border-line">
              {availableTables.map((table) => {
                const selected = selectedTableId === table.id;
                const fit =
                  table.capacity < party.party_size
                    ? { label: 'Too small', cls: 'text-danger' }
                    : table.capacity === party.party_size
                      ? { label: 'Exact fit', cls: 'text-seated' }
                      : { label: `${table.capacity - party.party_size} spare`, cls: 'text-ink-3' };

                return (
                  <label
                    key={table.id}
                    className={`flex cursor-pointer items-center gap-3 px-3.5 py-2.5 transition-colors ${
                      selected ? 'bg-accent-soft' : 'hover:bg-subtle'
                    }`}
                  >
                    <input
                      type="radio"
                      name="table"
                      value={table.id}
                      checked={selected}
                      onChange={() => setSelectedTableId(table.id)}
                      className="size-4 accent-accent"
                    />
                    <span className="flex-1 text-sm font-medium text-ink">{table.name}</span>
                    <span className="num text-[13px] text-ink-2">{table.capacity} seats</span>
                    <span className={`num w-20 text-right text-[12px] ${fit.cls}`}>{fit.label}</span>
                  </label>
                );
              })}
            </div>
          </fieldset>
        )}
      </div>

      <ModalFooter>
        <button type="button" onClick={close} className="btn btn-secondary">
          Cancel
        </button>
        <button
          type="button"
          disabled={!selectedTableId || isSeating}
          onClick={handleSeat}
          className="btn btn-dark"
        >
          {isSeating ? 'Seating…' : 'Seat party'}
        </button>
      </ModalFooter>
    </Modal>
  );
};
