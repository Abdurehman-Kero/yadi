"use client";

import { type ReactNode, useEffect, useId, useRef } from "react";

type Props = { title: string; onClose: () => void; children: ReactNode };

/** The browser's own dialog: it traps focus, closes on Escape and returns focus afterwards. */
export function Modal({ title, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = ref.current;
    const opener = document.activeElement;
    if (dialog && !dialog.open) dialog.showModal();
    return () => {
      if (dialog?.open) dialog.close();
      // React removes the dialog first, so the browser cannot restore focus on its own.
      if (opener instanceof HTMLElement && opener.isConnected) opener.focus();
    };
  }, []);

  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby={titleId}
      onCancel={(event) => {
        // The parent owns whether this is open, so Escape goes through it.
        event.preventDefault();
        onClose();
      }}
    >
      <div className="modal-header">
        <h2 id={titleId}>{title}</h2>
        <button type="button" className="button-quiet" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="modal-body">{children}</div>
    </dialog>
  );
}
