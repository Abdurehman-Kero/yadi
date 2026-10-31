"use client";

import { useState } from "react";
import { Modal } from "@/components/Modal";
import {
  errorMessage,
  listTaskEvents,
  type Task,
  type TaskEvent,
  type TaskStatus,
} from "@/lib/api";
import { formatDateTime, formatTime } from "@/lib/time";
import { PRIORITIES } from "./TaskForm";

const STATUS_LABELS: Record<TaskStatus, string> = {
  inbox: "Inbox",
  planned: "Planned",
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

  const finished = task.status === "completed" || task.status === "cancelled";
  const overdue = !finished && task.dueAt !== null && new Date(task.dueAt).getTime() < now;
  const priority = PRIORITIES.find((option) => option.value === task.priority)?.label;

  async function toggleHistory() {
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
    <li className="task-row">
      <div className="task-main">
        <h3 className="task-title">{task.title}</h3>
        <p className="task-meta">
          <span className="badge">{STATUS_LABELS[task.status]}</span>
          <span className={`badge priority-${task.priority}`}>{priority} priority</span>
          {task.fixedStartAt && task.fixedEndAt && (
            <>
              <span className="badge badge-fixed">Fixed</span>
              <span>
                {formatDateTime(task.fixedStartAt, timeZone)} –{" "}
                {formatTime(task.fixedEndAt, timeZone)}
              </span>
            </>
          )}
          {task.dueAt && <span>Due {formatDateTime(task.dueAt, timeZone)}</span>}
          {overdue && <span className="overdue">Overdue</span>}
          {task.estimatedMinutes !== null && <span>{task.estimatedMinutes} min</span>}
          {task.preferredPeriod && <span>Prefers {task.preferredPeriod}</span>}
          {!task.reminderEnabled && <span>No reminder</span>}
        </p>
        {task.description && <p className="task-notes">{task.description}</p>}
      </div>

      <div className="actions">
        {!finished && task.status !== "in_progress" && (
          <button type="button" disabled={busy} onClick={onStart}>
            Start<span className="visually-hidden"> {task.title}</span>
          </button>
        )}
        {!finished && (
          <button type="button" disabled={busy} onClick={onComplete}>
            Complete<span className="visually-hidden"> {task.title}</span>
          </button>
        )}
        {task.status === "completed" && (
          <button type="button" disabled={busy} onClick={onReopen}>
            Reopen<span className="visually-hidden"> {task.title}</span>
          </button>
        )}
        {!finished && (
          <>
            <button type="button" disabled={busy} onClick={onEdit}>
              Edit<span className="visually-hidden"> {task.title}</span>
            </button>
            <button
              type="button"
              className="button-quiet"
              disabled={busy}
              onClick={() => setConfirming(true)}
            >
              Cancel task<span className="visually-hidden"> {task.title}</span>
            </button>
          </>
        )}
        <button
          type="button"
          className="button-quiet"
          aria-expanded={events !== null}
          onClick={toggleHistory}
        >
          History<span className="visually-hidden"> of {task.title}</span>
        </button>
      </div>

      {confirming && (
        <Modal title="Cancel this task?" onClose={() => setConfirming(false)}>
          <p>
            &ldquo;{task.title}&rdquo; will move to Cancelled. This cannot be undone, and its
            reminders will stop.
          </p>
          <div className="actions">
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
            <button type="button" onClick={() => setConfirming(false)}>
              Keep task
            </button>
          </div>
        </Modal>
      )}

      {historyError && (
        <p className="message message-error" role="alert">
          {historyError}
        </p>
      )}
      {events && (
        <ol className="history">
          {events.map((event) => (
            <li key={event.id}>
              {EVENT_LABELS[event.type] ?? event.type} · {formatDateTime(event.at, timeZone)}
            </li>
          ))}
        </ol>
      )}
    </li>
  );
}
