import type { Metadata } from "next";
import { HealthStatus } from "@/features/health/HealthStatus";
import { NotificationSettings } from "@/features/settings/NotificationSettings";
import { SettingsScreen } from "@/features/settings/SettingsScreen";

export const metadata: Metadata = { title: "Settings · Yadi" };

export default function SettingsPage() {
  return (
    <>
      <h1>Settings</h1>
      <SettingsScreen />
      <NotificationSettings />
      <section className="panel" aria-labelledby="system-status">
        <h2 id="system-status">System status</h2>
        <HealthStatus />
      </section>
    </>
  );
}
