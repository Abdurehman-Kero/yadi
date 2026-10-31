"use client";

import { type FormEvent, useId, useState } from "react";
import { Modal } from "@/components/Modal";
import { errorMessage, updateBlock, type ScheduleBlock } from "@/lib/api";
import { formatDay, formatTime, utcToWallTime, wallTimeToUtc } from "@/lib/time";

type Props = {
  block: ScheduleBlock;
  timeZone: string;
  onClose: () => void;
  onMoved: (startAt: string) => void;
};

/** Why a block is where it is, and the way to move it. */
export function BlockDetails({ block, timeZone, onClose, onMoved }: Props) {
  const id = useId();
  const [start, setStart] = useState(() => utcToWallTime(block.startAt, timeZone));
  const [end, setEnd] = useState(() => utcToWallTime(block.endAt, timeZone));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const startAt = wallTimeToUtc(start, timeZone);
      await updateBlock(block.id, { startAt, endAt: wallTimeToUtc(end, timeZone) });
      onMoved(startAt);
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal title={block.title} onClose={onClose}>
      <p>
        <strong>{formatDay(block.startAt, timeZone)}</strong>, {formatTime(block.startAt, timeZone)}{" "}
        – {formatTime(block.endAt, timeZone)}
      </p>
      <p className="task-meta">
        <span className={`badge${block.isFixed ? " badge-fixed" : ""}`}>
          {block.isFixed ? "Fixed" : "Flexible"}
        </span>
        {block.locked && !block.isFixed && <span className="badge">Kept in place</span>}
      </p>
      <div>
        <h3 className="eyebrow">Why it is here</h3>
        <p>{block.reason}</p>
      </div>
      {block.isFixed ? (
        <p className="hint">To change a fixed time, edit the task, or ask Yadi to move it.</p>
      ) : (
        <form className="task-form" onSubmit={handleSubmit}>
          <h3 className="eyebrow">Move it</h3>
          <div className="field-row">
            <div className="field">
              <label htmlFor={`${id}-start`}>New start</label>
              <input
                id={`${id}-start`}
                type="datetime-local"
                value={start}
                onChange={(event) => setStart(event.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor={`${id}-end`}>New end</label>
              <input
                id={`${id}-end`}
                type="datetime-local"
                value={end}
                onChange={(event) => setEnd(event.target.value)}
              />
            </div>
          </div>
          {error && (
            <p className="message message-error" role="alert">
              {error}
            </p>
          )}
          <div className="form-actions">
            <button type="submit" className="button-primary" disabled={saving}>
              {saving ? "Saving…" : "Save time"}
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
}
