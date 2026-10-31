// Dates are entered and shown in the timezone saved in the user's settings, not the browser's.

function zoneOffsetMs(instant: Date, timeZone: string): number {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    hourCycle: "h23",
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
  }).formatToParts(instant);
  const get = (type: string) => Number(parts.find((part) => part.type === type)?.value);
  const asUtc = Date.UTC(
    get("year"),
    get("month") - 1,
    get("day"),
    get("hour"),
    get("minute"),
    get("second"),
  );
  return asUtc - Math.floor(instant.getTime() / 1000) * 1000;
}

/** Converts "YYYY-MM-DDTHH:mm" in `timeZone` to a UTC ISO string. */
export function wallTimeToUtc(wallTime: string, timeZone: string): string {
  const [date, time] = wallTime.split("T");
  const [year, month, day] = date.split("-").map(Number);
  const [hour, minute] = time.split(":").map(Number);
  const guess = Date.UTC(year, month - 1, day, hour, minute);
  // Two passes: the offset at the first estimate can differ across a daylight-saving change.
  const first = guess - zoneOffsetMs(new Date(guess), timeZone);
  const second = guess - zoneOffsetMs(new Date(first), timeZone);
  return new Date(second).toISOString();
}

/** Converts a UTC ISO string to "YYYY-MM-DDTHH:mm" in `timeZone`, for a datetime-local input. */
export function utcToWallTime(iso: string, timeZone: string): string {
  const instant = new Date(iso);
  return new Date(instant.getTime() + zoneOffsetMs(instant, timeZone)).toISOString().slice(0, 16);
}

export function formatDateTime(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    timeZone,
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function formatTime(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone, hour: "2-digit", minute: "2-digit" }).format(
    new Date(iso),
  );
}

export function formatDay(iso: string, timeZone: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    timeZone,
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date(iso));
}

/** The calendar day of an instant in `timeZone`, as "YYYY-MM-DD". */
export function dayKey(iso: string, timeZone: string): string {
  return utcToWallTime(iso, timeZone).slice(0, 10);
}
