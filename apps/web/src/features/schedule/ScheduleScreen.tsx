"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  errorMessage,
  generateSchedule,
  getPreferences,
  getSchedule,
  type Schedule,
  type ScheduleBlock,
} from "@/lib/api";
import { dayKey, formatDay } from "@/lib/time";
import { BlockRow } from "./BlockRow";
import { ScheduleNotices } from "./ScheduleNotices";

function groupByDay(blocks: ScheduleBlock[], timeZone: string) {
  const days = new Map<string, ScheduleBlock[]>();
  for (const block of blocks) {
    const key = dayKey(block.startAt, timeZone);
    days.set(key, [...(days.get(key) ?? []), block]);
  }
  return [...days.values()];
}

export function ScheduleScreen() {
  const [timeZone, setTimeZone] = useState<string | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let current = true;
    Promise.all([getPreferences(), getSchedule()])
      .then(([preferences, loaded]) => {
        if (!current) return;
        setTimeZone(preferences.timezone);
        setSchedule(loaded);
        setLoadError(null);
      })
      .catch((error) => {
        if (current) setLoadError(errorMessage(error));
      });
    return () => {
      current = false;
    };
  }, [attempt]);

  async function plan() {
    setWorking(true);
    setActionError(null);
    setNotice(null);
    try {
      const result = await generateSchedule();
      setSchedule(result);
      setNotice(
        result.unscheduled.length > 0
          ? `Plan updated. ${result.unscheduled.length} not in the plan: see below.`
          : "Plan updated.",
      );
    } catch (error) {
      setActionError(errorMessage(error));
    } finally {
      setWorking(false);
    }
  }

  const header = (
    <header className="page-header">
      <div>
        <h1>Schedule</h1>
        <p className="page-subtitle">
          {timeZone ? `Your next 7 days. Times are in ${timeZone}.` : "Your next 7 days."}
        </p>
      </div>
      {schedule && (
        <button type="button" className="button-primary" onClick={plan} disabled={working}>
          {working ? "Planning…" : schedule.generatedAt ? "Replan" : "Plan my week"}
        </button>
      )}
    </header>
  );

  if (loadError) {
    return (
      <>
        {header}
        <div className="message message-error" role="alert">
          <p>{loadError}</p>
          <button
            type="button"
            onClick={() => {
              setLoadError(null);
              setAttempt((value) => value + 1);
            }}
          >
            Try again
          </button>
        </div>
      </>
    );
  }
  if (!schedule || !timeZone) {
    return (
      <>
        {header}
        <p role="status">Loading your schedule…</p>
      </>
    );
  }

  return (
    <>
      {header}
      <p className="live-region" role="status">
        {notice}
      </p>
      {actionError && (
        <p className="message message-error" role="alert">
          {actionError}
        </p>
      )}
      {schedule.stale && (
        <p className="message message-warning">
          Your tasks changed since this plan was made. Replan to include the changes.
        </p>
      )}
      <ScheduleNotices schedule={schedule} timeZone={timeZone} />
      {schedule.blocks.length === 0 ? (
        <section className="panel">
          <h2>Nothing planned yet</h2>
          <p className="empty">
            Add <Link href="/tasks">tasks</Link> with an estimate, then choose{" "}
            {schedule.generatedAt ? "Replan" : "Plan my week"}.
          </p>
        </section>
      ) : (
        groupByDay(schedule.blocks, timeZone).map((blocks) => (
          <section
            className="panel"
            key={blocks[0].id}
            aria-label={formatDay(blocks[0].startAt, timeZone)}
          >
            <h2 className="day-heading">{formatDay(blocks[0].startAt, timeZone)}</h2>
            <ul className="block-list">
              {blocks.map((block) => (
                <BlockRow
                  key={`${block.id}-${block.startAt}`}
                  block={block}
                  timeZone={timeZone}
                  onMoved={() => {
                    setNotice("Time saved. Yadi keeps it when replanning.");
                    setAttempt((value) => value + 1);
                  }}
                />
              ))}
            </ul>
          </section>
        ))
      )}
    </>
  );
}
