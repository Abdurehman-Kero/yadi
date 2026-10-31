"use client";

import { type FormEvent, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  errorMessage,
  getPreferences,
  savePreferences,
  type Preferences,
} from "@/lib/api";

const NUMBER_FIELDS = ["defaultReminderMinutes", "bufferMinutes"] as const;

export function SettingsScreen() {
  const [form, setForm] = useState<Preferences | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [attempt, setAttempt] = useState(0);

  const browserZone = useMemo(() => Intl.DateTimeFormat().resolvedOptions().timeZone, []);
  const zones = useMemo(() => Intl.supportedValuesOf("timeZone"), []);

  useEffect(() => {
    let current = true;
    getPreferences()
      .then((preferences) => {
        if (current) setForm(preferences);
      })
      .catch((error) => {
        if (current) setLoadError(errorMessage(error));
      });
    return () => {
      current = false;
    };
  }, [attempt]);

  if (loadError) {
    return (
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
    );
  }
  if (!form) return <p role="status">Loading your settings…</p>;

  function update<K extends keyof Preferences>(key: K, value: Preferences[K]) {
    setForm((previous) => (previous ? { ...previous, [key]: value } : previous));
    setNotice(null);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!form) return;
    setSaving(true);
    setSaveError(null);
    setNotice(null);
    try {
      setForm(await savePreferences(form));
      setNotice("Settings saved.");
    } catch (error) {
      setSaveError(
        error instanceof ApiError && error.details.length > 0
          ? error.details.map((detail) => detail.issue).join(" ")
          : errorMessage(error),
      );
    } finally {
      setSaving(false);
    }
  }

  // Browsers can omit "UTC" from their list, and the saved zone must always be selectable.
  const options = [...new Set(["UTC", form.timezone, ...zones])];
  const labels: Record<(typeof NUMBER_FIELDS)[number], string> = {
    defaultReminderMinutes: "Default reminder, minutes before",
    bufferMinutes: "Gap between tasks, minutes",
  };

  return (
    <form className="panel task-form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="timezone">Timezone</label>
        <select
          id="timezone"
          value={form.timezone}
          onChange={(event) => update("timezone", event.target.value)}
        >
          {options.map((zone) => (
            <option key={zone} value={zone}>
              {zone}
            </option>
          ))}
        </select>
        {browserZone !== form.timezone && (
          <p className="hint">
            This device is set to {browserZone}.{" "}
            <button type="button" onClick={() => update("timezone", browserZone)}>
              Use {browserZone}
            </button>
          </p>
        )}
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor="work-start">Working hours start</label>
          <input
            id="work-start"
            type="time"
            value={form.workStart.slice(0, 5)}
            onChange={(event) => update("workStart", event.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="work-end">Working hours end</label>
          <input
            id="work-end"
            type="time"
            value={form.workEnd.slice(0, 5)}
            onChange={(event) => update("workEnd", event.target.value)}
          />
        </div>
      </div>
      <div className="field-row">
        {NUMBER_FIELDS.map((key) => (
          <div className="field" key={key}>
            <label htmlFor={key}>{labels[key]}</label>
            <input
              id={key}
              type="number"
              min={0}
              value={form[key]}
              onChange={(event) => update(key, Number(event.target.value))}
            />
          </div>
        ))}
      </div>
      {saveError && (
        <p className="message message-error" role="alert">
          {saveError}
        </p>
      )}
      <p className="live-region" role="status">
        {notice}
      </p>
      <div className="actions">
        <button type="submit" className="button-primary" disabled={saving}>
          {saving ? "Saving…" : "Save settings"}
        </button>
      </div>
    </form>
  );
}
