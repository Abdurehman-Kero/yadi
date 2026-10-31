import type { Schedule } from "@/lib/api";
import { formatDateTime } from "@/lib/time";

/** What the plan could not do: never hidden, always with a way forward. */
export function ScheduleNotices({ schedule, timeZone }: { schedule: Schedule; timeZone: string }) {
  if (schedule.unscheduled.length === 0 && schedule.conflicts.length === 0) return null;
  return (
    <section className="panel" aria-labelledby="not-planned">
      <h2 id="not-planned">Not in the plan</h2>
      <ul className="attention-list">
        {schedule.conflicts.map((conflict) => (
          <li className="attention-item" key={`${conflict.firstTitle}-${conflict.startAt}`}>
            <h3>
              {conflict.firstTitle} overlaps {conflict.secondTitle}
            </h3>
            <p className="hint">
              Both are fixed, at {formatDateTime(conflict.startAt, timeZone)}. Yadi will not move
              them; change one of the tasks.
            </p>
          </li>
        ))}
        {schedule.unscheduled.map((item) => (
          <li className="attention-item" key={item.taskId}>
            <h3>{item.title}</h3>
            <p className="hint">{item.detail}</p>
            <p className="hint">Options: {item.alternatives.join(" · ")}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
