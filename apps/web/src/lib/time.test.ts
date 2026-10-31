import { describe, expect, it } from "vitest";
import { dayKey, formatDateTime, formatTime, utcToWallTime, wallTimeToUtc } from "./time";

describe("wallTimeToUtc", () => {
  it("handles a zone without daylight saving", () => {
    expect(wallTimeToUtc("2030-01-15T10:00", "Africa/Addis_Ababa")).toBe(
      "2030-01-15T07:00:00.000Z",
    );
  });

  it("uses the right offset on each side of a daylight-saving change", () => {
    // New York moved to daylight time at 02:00 on 10 March 2030.
    expect(wallTimeToUtc("2030-03-10T01:30", "America/New_York")).toBe("2030-03-10T06:30:00.000Z");
    expect(wallTimeToUtc("2030-03-10T03:30", "America/New_York")).toBe("2030-03-10T07:30:00.000Z");
    expect(wallTimeToUtc("2030-07-01T09:00", "America/New_York")).toBe("2030-07-01T13:00:00.000Z");
  });

  it("does not throw on a local time skipped by the clock change", () => {
    expect(wallTimeToUtc("2030-03-10T02:30", "America/New_York")).toMatch(/^2030-03-10T0[67]:30/);
  });
});

describe("utcToWallTime", () => {
  it("round-trips through the user's zone, not the browser's", () => {
    for (const zone of ["UTC", "Africa/Addis_Ababa", "America/New_York", "Asia/Kolkata"]) {
      const wall = "2030-11-20T23:45";
      expect(utcToWallTime(wallTimeToUtc(wall, zone), zone)).toBe(wall);
    }
  });

  it("can land on a different calendar day than UTC", () => {
    expect(utcToWallTime("2030-01-15T22:30:00Z", "Africa/Addis_Ababa")).toBe("2030-01-16T01:30");
  });
});

describe("day and time helpers", () => {
  it("uses the user's zone for the calendar day", () => {
    expect(dayKey("2030-01-15T22:30:00Z", "Africa/Addis_Ababa")).toBe("2030-01-16");
    expect(dayKey("2030-01-15T22:30:00Z", "UTC")).toBe("2030-01-15");
    expect(formatTime("2030-01-15T22:30:00Z", "Africa/Addis_Ababa")).toBe("01:30");
  });
});

describe("formatDateTime", () => {
  it("shows the time in the given zone", () => {
    expect(formatDateTime("2030-01-15T07:00:00Z", "Africa/Addis_Ababa")).toContain("10:00");
    expect(formatDateTime("2030-01-15T07:00:00Z", "UTC")).toContain("07:00");
  });
});
