"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Modal } from "@/components/Modal";
import {
  cancelTask,
  completeTask,
  createTask,
  errorMessage,
  getPreferences,
  listTasks,
  reopenTask,
  startTask,
  updateTask,
  type Task,
  type TaskStatus,
} from "@/lib/api";
import { TaskForm } from "./TaskForm";
import { TaskRow } from "./TaskRow";

const VIEWS = {
  Active: ["inbox", "planned", "scheduled", "in_progress"],
  Completed: ["completed"],
  Cancelled: ["cancelled"],
} satisfies Record<string, TaskStatus[]>;
type View = keyof typeof VIEWS;

const EMPTY_MESSAGES: Record<View, string> = {
  Active: "Nothing to do yet. Add your first task above.",
  Completed: "No completed tasks yet.",
  Cancelled: "No cancelled tasks.",
};

export function TasksScreen() {
  const [timeZone, setTimeZone] = useState<string | null>(null);
  const [view, setView] = useState<View>("Active");
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [attempt, setAttempt] = useState(0);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    let current = true; // Ignores a slow response after the user has switched views.
    Promise.all([getPreferences(), listTasks(VIEWS[view])])
      .then(([preferences, page]) => {
        if (!current) return;
        setTimeZone(preferences.timezone);
        setTasks(page.items);
        setNextCursor(page.nextCursor);
        setNow(Date.now());
        setLoadError(null);
      })
      .catch((error) => {
        if (current) setLoadError(errorMessage(error));
      });
    return () => {
      current = false;
    };
  }, [view, attempt]);

  function chooseView(next: View) {
    setView(next);
    setTasks(null);
    setLoadError(null);
    setEditingId(null);
    setNotice(null);
    setActionError(null);
  }

  function retry() {
    setLoadError(null);
    setAttempt((value) => value + 1);
  }

  const applyResult = useCallback(
    (updated: Task) => {
      const stillInView = (VIEWS[view] as TaskStatus[]).includes(updated.status);
      setTasks((list) =>
        (list ?? []).flatMap((task) =>
          task.id !== updated.id ? [task] : stillInView ? [updated] : [],
        ),
      );
    },
    [view],
  );

  async function runAction(
    task: Task,
    action: (id: string) => Promise<Task>,
    done: (title: string) => string,
  ) {
    setBusyId(task.id);
    setActionError(null);
    setNotice(null);
    try {
      applyResult(await action(task.id));
      setNotice(done(task.title));
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setBusyId(null);
    }
  }

  async function loadMore() {
    try {
      const page = await listTasks(VIEWS[view], nextCursor);
      setTasks((list) => [...(list ?? []), ...page.items]);
      setNextCursor(page.nextCursor);
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  if (loadError) {
    return (
      <div className="message message-error" role="alert">
        <p>{loadError}</p>
        <button type="button" onClick={retry}>
          Try again
        </button>
      </div>
    );
  }
  if (!timeZone) return <p role="status">Loading your tasks…</p>;
  const editing = tasks?.find((task) => task.id === editingId);

  return (
    <>
      <div className="page-header">
        <p className="page-subtitle">
          Times are in {timeZone}. <Link href="/settings">Change timezone</Link>
        </p>
        <button type="button" className="button-primary" onClick={() => setAdding(true)}>
          New task
        </button>
      </div>

      {adding && (
        <Modal title="New task" onClose={() => setAdding(false)}>
          <TaskForm
            timeZone={timeZone}
            submitLabel="Add task"
            onDiscard={() => setAdding(false)}
            discardLabel="Close"
            onSubmit={async (values) => {
              setNotice(null);
              const created = await createTask(values);
              if (view === "Active") {
                setTasks((list) => [created, ...(list ?? [])]);
                setNow(Date.now());
              }
              setAdding(false);
              setNotice(`Added "${created.title}".`);
            }}
          />
        </Modal>
      )}

      <p className="live-region" role="status">
        {notice}
      </p>
      {actionError && (
        <p className="message message-error" role="alert">
          {actionError}
        </p>
      )}

      <section aria-labelledby="your-tasks" className="panel">
        <h2 id="your-tasks" className="visually-hidden">
          Your tasks
        </h2>
        <div className="segmented" role="group" aria-label="Filter tasks">
          {(Object.keys(VIEWS) as View[]).map((name) => (
            <button
              key={name}
              type="button"
              aria-pressed={view === name}
              onClick={() => chooseView(name)}
            >
              {name}
            </button>
          ))}
        </div>

        {tasks === null ? (
          <p role="status">Loading your tasks…</p>
        ) : tasks.length === 0 ? (
          <p className="empty">{EMPTY_MESSAGES[view]}</p>
        ) : (
          <ul className="task-list">
            {tasks.map((task) => (
              <TaskRow
                key={task.id}
                task={task}
                timeZone={timeZone}
                now={now}
                busy={busyId === task.id}
                onStart={() => runAction(task, startTask, (title) => `Started "${title}".`)}
                onComplete={() => runAction(task, completeTask, (title) => `Completed "${title}".`)}
                onReopen={() => runAction(task, reopenTask, (title) => `Reopened "${title}".`)}
                onCancel={() => runAction(task, cancelTask, (title) => `Cancelled "${title}".`)}
                onEdit={() => setEditingId(task.id)}
              />
            ))}
          </ul>
        )}
        {nextCursor && (
          <button type="button" onClick={loadMore}>
            Show more
          </button>
        )}
      </section>

      {editing && (
        <Modal title="Edit task" onClose={() => setEditingId(null)}>
          <TaskForm
            task={editing}
            timeZone={timeZone}
            submitLabel="Save changes"
            onDiscard={() => setEditingId(null)}
            onSubmit={async (values) => {
              applyResult(await updateTask(editing.id, values));
              setEditingId(null);
              setNotice(`Saved "${values.title}".`);
            }}
          />
        </Modal>
      )}
    </>
  );
}
