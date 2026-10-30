import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { HealthStatus } from "./HealthStatus";

function mockFetch(impl: () => Promise<unknown>) {
  vi.stubGlobal("fetch", vi.fn(impl));
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("HealthStatus", () => {
  it("shows a loading state first", () => {
    mockFetch(() => new Promise(() => {}));
    render(<HealthStatus />);
    expect(screen.getByRole("status")).toHaveTextContent("Checking");
  });

  it("shows ok when the API and database answer", async () => {
    mockFetch(async () => ({ ok: true, json: async () => ({ status: "ok", database: "ok" }) }));
    render(<HealthStatus />);
    expect(await screen.findByText(/API: ok/)).toHaveTextContent("Database: ok");
  });

  it("shows the API's error message when the database is down", async () => {
    mockFetch(async () => ({
      ok: false,
      json: async () => ({ error: { message: "Database is not available." } }),
    }));
    render(<HealthStatus />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Database is not available.");
  });

  it("shows an error when the API cannot be reached", async () => {
    mockFetch(async () => {
      throw new TypeError("network");
    });
    render(<HealthStatus />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not reach");
  });
});
