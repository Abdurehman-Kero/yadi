"use client";

import { useRef, useState } from "react";
import { Modal } from "@/components/Modal";
import {
  errorMessage,
  listTaskEvents,
  type Task,
  type TaskEvent,
  type TaskStatus,
} from "@/lib/api";
import { formatDateTime, formatTime } from "@/lib/time";

// Plain words for what each status means to the person, not to the system.
const STATUS_LABELS: Record<TaskStatus, string> = {
  inbox: "Needs details",
  planned: "Ready to plan",
  scheduled: "Scheduled",
  in_progress: "In progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

const EVENT_LABELS: Record<string, string> = {
  created: "Created",
  updated: "Edited",
  started: "Started",
  completed: "Completed",
  reopened: "Reopened",
  cancelled: "Cancelled",
  scheduled: "Scheduled by Yadi",
  unscheduled: "Removed from the plan",
  rescheduled: "Moved",
};

type Props = {
  task: Task;
  timeZone: string;
  now: number;
  busy: boolean;
  onStart: () => void;
  onComplete: () => void;
  onReopen: () => void;
  onEdit: () => void;
  onCancel: () => void;
};

export function TaskRow({
  task,
  timeZone,
  now,
  busy,
  onStart,
  onComplete,
  onReopen,
  onEdit,
  onCancel,
}: Props) {
  const [confirming, setConfirming] = useState(false);
  const [events, setEvents] = useState<TaskEvent[] | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const menu = useRef<HTMLDetailsElement>(null);

  const finished = task.status === "completed" || task.status === "cancelled";
  const overdue = !finished && task.dueAt !== null && new Date(task.dueAt).getTime() < now;
  const important = task.priority === "critical" || task.priority === "high";

  function closeMenu() {
    if (menu.current) menu.current.open = false;
  }

  async function toggleHistory() {
    closeMenu();
    if (events) {
      setEvents(null);
      return;
    }
    setHistoryError(null);
    try {
      setEvents(await listTaskEvents(task.id));
    } catch (error) {
      setHistoryError(errorMessage(error));
    }
  }

  return (
    <li className={`task-row${finished ? " task-finished" : ""}`}>
      {!finished ? (
        <button
          type="button"
          className="check-button"
          disabled={busy}
          onClick={onComplete}
          title="Mark as complete"
        >
          <span className="visually-hidden">Complete {task.title}</span>
        </button>
      ) : (
        <span className="check-done" aria-hidden="true">
          {task.status === "completed" ? "✓" : "–"}
        </span>
      )}

      <div className="task-main">
        <h3 className="task-title">{task.title}</h3>
        <p className="task-meta">
          {task.fixedStartAt && task.fixedEndAt && (
            <span>
              <span className="badge badge-fixed">Fixed</span>{" "}
              {formatDateTime(task.fixedStartAt, timeZone)} –{" "}
              {formatTime(task.fixedEndAt, timeZone)}
            </span>
          )}
          {task.dueAt && (
            <span className={overdue ? "overdue" : undefined}>
              {overdue ? "Overdue · due " : "Due "}
              {formatDateTime(task.dueAt, timeZone)}
            </span>
          )}
          {task.estimatedMinutes !== null && <span>{task.estimatedMinutes} min</span>}
          {task.preferredPeriod && <span>Prefers {task.preferredPeriod}</span>}
          {!task.reminderEnabled && <span>No reminder</span>}
        </p>
        {task.description && <p className="task-notes">{task.description}</p>}
        {historyError && (
          <p className="message message-error" role="alert">
            {historyError}
          </p>
        )}
        {events && (
          <ol className="history" aria-label={`History of ${task.title}`}>
            {events.map((event) => (
              <li key={event.id}>
                {EVENT_LABELS[event.type] ?? event.type} · {formatDateTime(event.at, timeZone)}
              </li>
            ))}
          </ol>
        )}
      </div>

      <div className="task-side">
        {important && (
          <span className={`badge priority-${task.priority}`}>
            {task.priority === "critical" ? "Critical" : "High"}
          </span>
        )}
        <span className="badge">{STATUS_LABELS[task.status]}</span>
        <div className="row-actions">
          {!finished && task.status !== "in_progress" && !task.fixedStartAt && (
            <button type="button" disabled={busy} onClick={onStart}>
              Start<span className="visually-hidden"> {task.title}</span>
            </button>
          )}
          {task.status === "completed" && (
            <button type="button" disabled={busy} onClick={onReopen}>
              Reopen<span className="visually-hidden"> {task.title}</span>
            </button>
          )}
          <details className="menu" ref={menu}>
            <summary aria-label={`More actions for ${task.title}`}>
              <span aria-hidden="true">•••</span>
            </summary>
            <div className="menu-items">
              {!finished && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    closeMenu();
                    onEdit();
                  }}
                >
                  Edit<span className="visually-hidden"> {task.title}</span>
                </button>
              )}
              <button type="button" aria-expanded={events !== null} onClick={toggleHistory}>
                History<span className="visually-hidden"> of {task.title}</span>
              </button>
              {!finished && (
                <button
                  type="button"
                  className="menu-danger"
                  disabled={busy}
                  onClick={() => {
                    closeMenu();
                    setConfirming(true);
                  }}
                >
                  Cancel task<span className="visually-hidden"> {task.title}</span>
                </button>
              )}
            </div>
          </details>
        </div>
      </div>

      {confirming && (
        <Modal title="Cancel this task?" onClose={() => setConfirming(false)}>
          <p>
            &ldquo;{task.title}&rdquo; will move to Cancelled. This cannot be undone, and its
            reminders will stop.
          </p>
          <div className="form-actions">
            <button type="button" onClick={() => setConfirming(false)}>
              Keep task
            </button>
            <button
              type="button"
              className="button-danger"
              disabled={busy}
              onClick={() => {
                setConfirming(false);
                onCancel();
              }}
            >
              Yes, cancel task
            </button>
          </div>
        </Modal>
      )}
    </li>
  );
}
