"use client";

import type { ScheduleBlock } from "@/lib/api";
import { formatTime, utcToWallTime } from "@/lib/time";

const HOUR_HEIGHT = 64;
const MIN_BLOCK_HEIGHT = 30;

type Props = {
  blocks: ScheduleBlock[];
  timeZone: string;
  workStart: string;
  workEnd: string;
  now: number;
  isToday: boolean;
  onSelect: (block: ScheduleBlock) => void;
};

function minutesOfDay(iso: string, timeZone: string): number {
  const wall = utcToWallTime(iso, timeZone);
  return Number(wall.slice(11, 13)) * 60 + Number(wall.slice(14, 16));
}

/** A day drawn to scale. Still a plain ordered list to assistive technology. */
export function DayTimeline({
  blocks,
  timeZone,
  workStart,
  workEnd,
  now,
  isToday,
  onSelect,
}: Props) {
  const placed = blocks.map((block) => {
    const start = minutesOfDay(block.startAt, timeZone);
    const end = minutesOfDay(block.endAt, timeZone);
    // A block running past midnight is drawn to the end of this day.
    return { block, start, end: end > start ? end : 24 * 60 };
  });
  const firstHour = Math.min(
    Number(workStart.slice(0, 2)),
    ...placed.map((p) => Math.floor(p.start / 60)),
  );
  const lastHour = Math.max(
    Math.ceil((Number(workEnd.slice(0, 2)) * 60 + Number(workEnd.slice(3, 5))) / 60),
    ...placed.map((p) => Math.ceil(p.end / 60)),
  );
  // One line more than the hours drawn, so the end of the last hour is marked too.
  const hours = Array.from({ length: lastHour - firstHour + 1 }, (_, index) => firstHour + index);
  const top = (minutes: number) => ((minutes - firstHour * 60) / 60) * HOUR_HEIGHT;
  const nowMinutes = minutesOfDay(new Date(now).toISOString(), timeZone);
  const showNow = isToday && nowMinutes >= firstHour * 60 && nowMinutes <= lastHour * 60;

  return (
    <div className="timeline" style={{ height: (hours.length - 1) * HOUR_HEIGHT + 12 }}>
      {hours.map((hour) => (
        <div
          className="timeline-hour"
          key={hour}
          style={{ top: top(hour * 60) }}
          aria-hidden="true"
        >
          <span>{String(hour).padStart(2, "0")}:00</span>
        </div>
      ))}
      {showNow && (
        <div className="timeline-now" style={{ top: top(nowMinutes) }} aria-hidden="true" />
      )}
      <ol className="timeline-blocks">
        {placed.map(({ block, start, end }, index) => {
          const overlapsPrevious = index > 0 && placed[index - 1].end > start;
          const past = new Date(block.endAt).getTime() < now;
          const important = block.priority === "critical" || block.priority === "high";
          return (
            <li
              key={block.id}
              className={[
                "timeline-block",
                block.isFixed ? "timeline-fixed" : "",
                past ? "timeline-past" : "",
                overlapsPrevious ? "timeline-overlap" : "",
              ].join(" ")}
              style={{
                top: top(start),
                height: Math.max(((end - start) / 60) * HOUR_HEIGHT - 3, MIN_BLOCK_HEIGHT),
              }}
            >
              <button type="button" onClick={() => onSelect(block)}>
                <h3 className="timeline-title">{block.title}</h3>
                <span className="timeline-time">
                  {formatTime(block.startAt, timeZone)} – {formatTime(block.endAt, timeZone)}
                  {block.isFixed ? " · Fixed" : " · Flexible"}
                  {block.locked && !block.isFixed && " · Kept in place"}
                  {important && ` · ${block.priority === "critical" ? "Critical" : "High"}`}
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
