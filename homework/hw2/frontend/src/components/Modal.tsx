import React, { useEffect, useId } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: React.ReactNode;
  children: React.ReactNode;
  variant?: 'dialog' | 'sheet';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  variant = 'dialog',
}) => {
  const titleId = useId();

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isSheet = variant === 'sheet';

  return (
    <div
      className={`fixed inset-0 z-50 flex bg-ink/35 ${
        isSheet ? 'justify-end' : 'items-start justify-center p-4 pt-[12vh]'
      }`}
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={
          isSheet
            ? 'flex h-full w-full max-w-[420px] flex-col border-l border-line bg-surface shadow-[-24px_0_48px_-24px_rgba(31,27,22,0.25)]'
            : 'w-full max-w-[460px] rounded-lg border border-line bg-surface shadow-[0_24px_64px_-16px_rgba(31,27,22,0.3)]'
        }
      >
        <div className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
          <div className="min-w-0">
            <h2 id={titleId} className="text-[15px] font-semibold tracking-[-0.01em] text-ink">
              {title}
            </h2>
            {description && <p className="mt-0.5 text-[13px] text-ink-2">{description}</p>}
          </div>
          <button onClick={onClose} className="btn btn-ghost btn-icon -mr-1.5 -mt-1" aria-label="Close">
            <X className="size-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

export const ModalFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex items-center justify-end gap-2 rounded-b-lg border-t border-line bg-subtle px-5 py-3">
    {children}
  </div>
);
