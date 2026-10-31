import type { ScheduleBlock } from "@/lib/api";
import { formatTime } from "@/lib/time";

/** One compact line of the plan, as shown on Today. Details live on the Schedule screen. */
export function BlockRow({ block, timeZone }: { block: ScheduleBlock; timeZone: string }) {
  return (
    <li className={`agenda-row${block.isFixed ? " agenda-fixed" : ""}`}>
      <span className="agenda-time">
        {formatTime(block.startAt, timeZone)} – {formatTime(block.endAt, timeZone)}
      </span>
      <span className="agenda-title">{block.title}</span>
      {block.isFixed && <span className="badge badge-fixed">Fixed</span>}
    </li>
  );
}
