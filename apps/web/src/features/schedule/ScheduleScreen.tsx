"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  errorMessage,
  generateSchedule,
  getPreferences,
  getSchedule,
  type Preferences,
  type Schedule,
  type ScheduleBlock,
} from "@/lib/api";
import { dayKey, formatShortDay } from "@/lib/time";
import { BlockDetails } from "./BlockDetails";
import { DayTimeline } from "./DayTimeline";
import { ScheduleNotices } from "./ScheduleNotices";

const DAYS_SHOWN = 7;

function nextDays(now: number, timeZone: string): { key: string; iso: string }[] {
  const seen = new Set<string>();
  const days = [];
  // Hourly steps across a week, so a 23- or 25-hour day can neither skip nor repeat a date.
  for (let hour = 0; days.length < DAYS_SHOWN; hour += 1) {
    const iso = new Date(now + hour * 3_600_000).toISOString();
    const key = dayKey(iso, timeZone);
    if (!seen.has(key)) {
      seen.add(key);
      days.push({ key, iso });
    }
  }
  return days;
}

export function ScheduleScreen() {
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [now, setNow] = useState(() => Date.now());
  const [chosenDay, setChosenDay] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    let current = true;
    Promise.all([getPreferences(), getSchedule()])
      .then(([loadedPreferences, loaded]) => {
        if (!current) return;
        setPreferences(loadedPreferences);
        setSchedule(loaded);
        setNow(Date.now());
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
      setChosenDay(null);
      setNow(Date.now());
      setNotice(
        result.unscheduled.length > 0
          ? `Plan updated. ${result.unscheduled.length} not in the plan.`
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
          {preferences ? `Times are in ${preferences.timezone}.` : "Your next 7 days."}
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
  if (!schedule || !preferences) {
    return (
      <>
        {header}
        <p role="status">Loading your schedule…</p>
      </>
    );
  }

  const timeZone = preferences.timezone;
  const byDay = new Map<string, ScheduleBlock[]>();
  for (const block of schedule.blocks) {
    const key = dayKey(block.startAt, timeZone);
    byDay.set(key, [...(byDay.get(key) ?? []), block]);
  }
  const days = nextDays(now, timeZone);
  const today = days[0].key;
  // Opens on today, or the first day with something on it if today is empty.
  const firstBusy = days.find((day) => byDay.has(day.key))?.key;
  const day = chosenDay ?? (byDay.has(today) ? today : (firstBusy ?? today));
  const blocks = byDay.get(day) ?? [];
  const selected = schedule.blocks.find((block) => block.id === selectedId);

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

      <div className="day-strip" role="group" aria-label="Choose a day">
        {days.map(({ key, iso }) => {
          const count = byDay.get(key)?.length ?? 0;
          return (
            <button
              key={key}
              type="button"
              className="day-tab"
              aria-pressed={key === day}
              onClick={() => setChosenDay(key)}
            >
              <span className="day-tab-name">
                {key === today ? "Today" : formatShortDay(iso, timeZone)}
              </span>
              <span className="day-tab-count">{count === 0 ? "Free" : `${count} planned`}</span>
            </button>
          );
        })}
      </div>

      <div className="schedule-layout">
        <section className="panel" aria-label={`Plan for ${day}`}>
          {!schedule.generatedAt && schedule.blocks.length === 0 ? (
            <div className="empty-state">
              <h2>Nothing planned yet</h2>
              <p>
                Add <Link href="/tasks">tasks</Link> with an estimate, then choose Plan my week.
                Yadi will fit them around your commitments.
              </p>
            </div>
          ) : (
            <>
              {blocks.length === 0 && <p className="empty">Nothing is planned on this day.</p>}
              <DayTimeline
                key={day}
                blocks={blocks}
                timeZone={timeZone}
                workStart={preferences.workStart}
                workEnd={preferences.workEnd}
                now={now}
                isToday={day === today}
                onSelect={(block) => setSelectedId(block.id)}
              />
            </>
          )}
        </section>
        <ScheduleNotices schedule={schedule} timeZone={timeZone} />
      </div>

      {selected && (
        <BlockDetails
          key={`${selected.id}-${selected.startAt}`}
          block={selected}
          timeZone={timeZone}
          onClose={() => setSelectedId(null)}
          onMoved={(startAt) => {
            setSelectedId(null);
            // Follow the block to its new day, so the result of the move is on screen.
            setChosenDay(dayKey(startAt, timeZone));
            setNotice("Time saved. Yadi keeps it when replanning.");
            setAttempt((value) => value + 1);
          }}
        />
      )}
    </>
  );
}
