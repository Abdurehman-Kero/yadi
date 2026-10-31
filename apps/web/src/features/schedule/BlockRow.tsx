"use client";

import { type FormEvent, useId, useState } from "react";
import { errorMessage, updateBlock, type ScheduleBlock } from "@/lib/api";
import { formatTime, utcToWallTime, wallTimeToUtc } from "@/lib/time";

type Props = {
  block: ScheduleBlock;
  timeZone: string;
  onMoved?: () => void;
};

export function BlockRow({ block, timeZone, onMoved }: Props) {
  const id = useId();
  const [moving, setMoving] = useState(false);
  const [start, setStart] = useState(() => utcToWallTime(block.startAt, timeZone));
  const [end, setEnd] = useState(() => utcToWallTime(block.endAt, timeZone));
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await updateBlock(block.id, {
        startAt: wallTimeToUtc(start, timeZone),
        endAt: wallTimeToUtc(end, timeZone),
      });
      setMoving(false);
      onMoved?.();
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className={`block-row${block.isFixed ? " block-fixed" : ""}`}>
      <p className="block-time">
        {formatTime(block.startAt, timeZone)} – {formatTime(block.endAt, timeZone)}
      </p>
      <div className="block-body">
        <h3>{block.title}</h3>
        <p className="task-meta">
          {block.isFixed ? (
            <span className="badge badge-fixed">Fixed</span>
          ) : (
            <span className="badge">Flexible</span>
          )}
          {block.locked && !block.isFixed && <span className="badge">Kept in place</span>}
          {(block.priority === "critical" || block.priority === "high") && (
            <span className={`badge priority-${block.priority}`}>
              {block.priority === "critical" ? "Critical" : "High"} priority
            </span>
          )}
        </p>
        <p className="block-reason">{block.reason}</p>
        {onMoved && !block.isFixed && !moving && (
          <div className="actions">
            <button type="button" className="button-quiet" onClick={() => setMoving(true)}>
              Move<span className="visually-hidden"> {block.title}</span>
            </button>
          </div>
        )}
        {moving && (
          <form className="task-form" onSubmit={handleSubmit}>
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
            <div className="actions">
              <button type="submit" className="button-primary" disabled={saving}>
                {saving ? "Saving…" : "Save time"}
              </button>
              <button type="button" onClick={() => setMoving(false)} disabled={saving}>
                Keep current time
              </button>
            </div>
          </form>
        )}
      </div>
    </li>
  );
}
