"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Modal } from "@/components/Modal";
import {
  completeTask,
  createTask,
  errorMessage,
  generateSchedule,
  getPreferences,
  getSchedule,
  listTasks,
  savePreferences,
  startTask,
  type Preferences,
  type Schedule,
  type Task,
} from "@/lib/api";
import { BlockRow } from "@/features/schedule/BlockRow";
import { ScheduleNotices } from "@/features/schedule/ScheduleNotices";
import { AssistantCapture } from "@/features/tasks/AssistantCapture";
import { TaskForm } from "@/features/tasks/TaskForm";
import { dayKey, formatDateTime, formatDay, formatTime } from "@/lib/time";

type Data = { preferences: Preferences; schedule: Schedule; tasks: Task[]; now: number };

const ACTIVE = ["inbox", "planned", "scheduled", "in_progress"] as const;

export function TodayScreen() {
  const [data, setData] = useState<Data | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    let current = true;
    Promise.all([getPreferences(), getSchedule(), listTasks([...ACTIVE])])
      .then(([preferences, schedule, page]) => {
        if (!current) return;
        setData({ preferences, schedule, tasks: page.items, now: Date.now() });
        setLoadError(null);
      })
      .catch((error) => {
        if (current) setLoadError(errorMessage(error));
      });
    return () => {
      current = false;
    };
  }, [attempt]);

  const reload = () => setAttempt((value) => value + 1);

  async function act(action: () => Promise<unknown>, done: string) {
    setWorking(true);
    setActionError(null);
    setNotice(null);
    try {
      await action();
      setNotice(done);
      reload();
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setWorking(false);
    }
  }

  if (loadError) {
    return (
      <>
        <h1>Today</h1>
        <div className="message message-error" role="alert">
          <p>{loadError}</p>
          <button type="button" onClick={reload}>
            Try again
          </button>
        </div>
      </>
    );
  }
  if (!data) {
    return (
      <>
        <h1>Today</h1>
        <p role="status">Loading your day…</p>
      </>
    );
  }

  const { preferences, schedule, tasks, now } = data;
  const timeZone = preferences.timezone;
  const browserZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const today = dayKey(new Date(now).toISOString(), timeZone);
  const remaining = schedule.blocks.filter((b) => new Date(b.endAt).getTime() > now);
  const todaysBlocks = remaining.filter((b) => dayKey(b.startAt, timeZone) === today);
  const next = remaining[0];
  const overdue = tasks.filter(
    (t) => t.dueAt && !t.fixedStartAt && new Date(t.dueAt).getTime() < now,
  );
  const upcoming = tasks
    .filter((t) => t.dueAt && new Date(t.dueAt).getTime() >= now)
    .sort((a, b) => (a.dueAt as string).localeCompare(b.dueAt as string))
    .slice(0, 4);
  const needsPlan = !next && tasks.length > 0;
  const isNew = tasks.length === 0 && schedule.blocks.length === 0;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Today</h1>
          <p className="page-subtitle">{formatDay(new Date(now).toISOString(), timeZone)}</p>
        </div>
        <div className="actions">
          <button type="button" onClick={() => setAdding(true)}>
            New task
          </button>
          <button
            type="button"
            className="button-primary"
            disabled={working}
            onClick={() => act(generateSchedule, "Plan updated.")}
          >
            {working ? "Planning…" : schedule.generatedAt ? "Replan" : "Plan my week"}
          </button>
        </div>
      </header>

      {adding && (
        <Modal title="New task" onClose={() => setAdding(false)}>
          <TaskForm
            timeZone={timeZone}
            submitLabel="Add task"
            onSubmit={async (values) => {
              const created = await createTask(values);
              setAdding(false);
              setNotice(`Added "${created.title}".`);
              reload();
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

      {timeZone === "UTC" && browserZone !== "UTC" && (
        <div className="message message-warning banner">
          <span>Times are showing in UTC. This device is set to {browserZone}.</span>
          <button
            type="button"
            disabled={working}
            onClick={() =>
              act(
                () => savePreferences({ ...preferences, timezone: browserZone }),
                `Times now use ${browserZone}.`,
              )
            }
          >
            Use {browserZone}
          </button>
        </div>
      )}

      <AssistantCapture
        timeZone={timeZone}
        onCreated={(task) => {
          setNotice(`Added "${task.title}".`);
          reload();
        }}
        onChanged={reload}
      />

      {schedule.stale && (
        <p className="message message-warning">
          Your tasks changed since this plan was made. Replan to include the changes.
        </p>
      )}

      {isNew ? (
        <section className="panel empty-state">
          <h2>Welcome to Yadi</h2>
          <p>
            Tell Yadi what is on your plate, in your own words. Then choose Plan my week, and Yadi
            will fit it around your commitments and remind you when it is time.
          </p>
        </section>
      ) : (
        <div className="grid-two">
          <div className="stack">
            {next ? (
              <section className="panel next-up" aria-labelledby="next-up">
                <p className="eyebrow" id="next-up">
                  Next up ·{" "}
                  {dayKey(next.startAt, timeZone) === today
                    ? ""
                    : `${formatDay(next.startAt, timeZone)} · `}
                  {formatTime(next.startAt, timeZone)} – {formatTime(next.endAt, timeZone)}
                </p>
                <p className="next-title">{next.title}</p>
                <div className="actions">
                  {next.status !== "in_progress" && (
                    <button
                      type="button"
                      disabled={working}
                      onClick={() => act(() => startTask(next.taskId), `Started "${next.title}".`)}
                    >
                      Start
                    </button>
                  )}
                  <button
                    type="button"
                    disabled={working}
                    onClick={() =>
                      act(() => completeTask(next.taskId), `Completed "${next.title}".`)
                    }
                  >
                    Complete
                  </button>
                </div>
              </section>
            ) : (
              needsPlan && (
                <section className="panel next-up" aria-labelledby="next-up">
                  <p className="eyebrow" id="next-up">
                    Next up
                  </p>
                  <p className="next-title">
                    {tasks.length} {tasks.length === 1 ? "task is" : "tasks are"} waiting for a plan
                  </p>
                  <p className="hint">Choose Plan my week, and Yadi will find time for them.</p>
                </section>
              )
            )}

            <section className="panel" aria-labelledby="today-schedule">
              <div className="panel-header">
                <h2 id="today-schedule">Rest of today</h2>
                <Link href="/schedule">Full schedule</Link>
              </div>
              {todaysBlocks.length === 0 ? (
                <p className="empty">Nothing else is planned for today.</p>
              ) : (
                <ul className="agenda">
                  {todaysBlocks.map((block) => (
                    <BlockRow key={block.id} block={block} timeZone={timeZone} />
                  ))}
                </ul>
              )}
            </section>
          </div>

          <div className="stack">
            {overdue.length > 0 && (
              <section className="panel panel-attention" aria-labelledby="overdue">
                <h2 id="overdue">Overdue</h2>
                <ul className="attention-list">
                  {overdue.map((task) => (
                    <li className="attention-item" key={task.id}>
                      <h3>{task.title}</h3>
                      <p className="hint">
                        <span className="overdue">Overdue</span> · was due{" "}
                        {formatDateTime(task.dueAt as string, timeZone)}
                      </p>
                    </li>
                  ))}
                </ul>
              </section>
            )}
            <ScheduleNotices
              compact
              schedule={{
                ...schedule,
                // Overdue tasks already have their own panel above.
                unscheduled: schedule.unscheduled.filter(
                  (item) => !overdue.some((task) => task.id === item.taskId),
                ),
              }}
              timeZone={timeZone}
            />
            <section className="panel" aria-labelledby="upcoming">
              <div className="panel-header">
                <h2 id="upcoming">Upcoming deadlines</h2>
                <Link href="/tasks">All tasks</Link>
              </div>
              {upcoming.length === 0 ? (
                <p className="empty">No deadlines coming up.</p>
              ) : (
                <ul className="attention-list">
                  {upcoming.map((task) => (
                    <li className="attention-item" key={task.id}>
                      <h3>{task.title}</h3>
                      <p className="hint">Due {formatDateTime(task.dueAt as string, timeZone)}</p>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </div>
      )}
    </>
  );
}
