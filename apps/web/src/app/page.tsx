import { HealthStatus } from "@/features/health/HealthStatus";

export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "4rem auto", padding: "0 1rem" }}>
      <h1>Yadi</h1>
      <p>Your personal assistant. Foundation build (M01) — no features yet.</p>
      <HealthStatus />
    </main>
  );
}
