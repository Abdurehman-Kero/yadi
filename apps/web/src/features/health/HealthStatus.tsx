"use client";

import { useEffect, useState } from "react";

type State =
  { kind: "loading" } | { kind: "ok"; database: string } | { kind: "error"; message: string };

export function HealthStatus({ endpoint = "/api/v1/health/ready" }: { endpoint?: string }) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    fetch(endpoint, { signal: controller.signal })
      .then(async (res) => {
        const body = await res.json();
        if (!res.ok) {
          setState({
            kind: "error",
            message: body?.error?.message ?? "The service is unavailable.",
          });
          return;
        }
        setState({ kind: "ok", database: body.database });
      })
      .catch((err: unknown) => {
        if ((err as Error).name === "AbortError") return;
        setState({ kind: "error", message: "Could not reach the Yadi API." });
      });
    return () => controller.abort();
  }, [endpoint]);

  if (state.kind === "loading") return <p role="status">Checking Yadi services…</p>;
  if (state.kind === "error") return <p role="alert">Problem: {state.message}</p>;
  return <p role="status">API: ok · Database: {state.database}</p>;
}
