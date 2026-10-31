"use client";

import { type FormEvent, useId, useState } from "react";
import { ApiError, errorMessage, type Task, type TaskCreate, type TaskPriority } from "@/lib/api";

import { utcToWallTime, wallTimeToUtc } from "@/lib/time";

export const PRIORITIES: { value: TaskPriority; label: string }[] = [
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
];

type Props = {
  task?: Task;
  initial?: TaskCreate;
  discardLabel?: string;
  timeZone: string;
  submitLabel: string;
  onSubmit: (values: Required<TaskCreate>) => Promise<void>;
  onDiscard?: () => void;
};

export function TaskForm({
  task,
  initial,
  discardLabel = "Discard changes",
  timeZone,
  submitLabel,
  onSubmit,
  onDiscard,
}: Props) {
  const id = useId();
  const start = task ?? initial;
  const [title, setTitle] = useState(start?.title ?? "");
  const [description, setDescription] = useState(start?.description ?? "");
  const [due, setDue] = useState(start?.dueAt ? utcToWallTime(start.dueAt, timeZone) : "");
  const [minutes, setMinutes] = useState(start?.estimatedMinutes?.toString() ?? "");
  const [priority, setPriority] = useState<TaskPriority>(start?.priority ?? "medium");
  const [isFixed, setIsFixed] = useState(Boolean(start?.fixedStartAt));
  const [fixedStart, setFixedStart] = useState(
    start?.fixedStartAt ? utcToWallTime(start.fixedStartAt, timeZone) : "",
  );
  const [fixedEnd, setFixedEnd] = useState(
    start?.fixedEndAt ? utcToWallTime(start.fixedEndAt, timeZone) : "",
  );
  const [period, setPeriod] = useState<string>(start?.preferredPeriod ?? "");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFieldErrors({});
    setFormError(null);
    if (!title.trim()) {
      setFieldErrors({ title: "Enter a title." });
      return;
    }
    if (isFixed && (!fixedStart || !fixedEnd)) {
      setFieldErrors({ fixedEndAt: "Enter both a start and an end." });
      return;
    }
    setSaving(true);
    try {
      await onSubmit({
        title,
        description: description.trim() ? description : null,
        priority,
        dueAt: due ? wallTimeToUtc(due, timeZone) : null,
        estimatedMinutes: minutes ? Number(minutes) : null,
        fixedStartAt: isFixed ? wallTimeToUtc(fixedStart, timeZone) : null,
        fixedEndAt: isFixed ? wallTimeToUtc(fixedEnd, timeZone) : null,
        preferredPeriod:
          isFixed || !period ? null : (period as Required<TaskCreate>["preferredPeriod"]),
      });
      if (!start) {
        setTitle("");
        setDescription("");
        setDue("");
        setMinutes("");
        setPriority("medium");
        setIsFixed(false);
        setFixedStart("");
        setFixedEnd("");
        setPeriod("");
      }
    } catch (error) {
      // What the user typed stays in the form so nothing has to be re-entered.
      if (error instanceof ApiError && error.details.length > 0) {
        setFieldErrors(Object.fromEntries(error.details.map((d) => [d.field, d.issue])));
      } else {
        setFormError(errorMessage(error));
      }
    } finally {
      setSaving(false);
    }
  }

  const describedBy = (field: string) => (fieldErrors[field] ? `${id}-${field}-error` : undefined);
  const fieldError = (field: string) =>
    fieldErrors[field] && (
      <p className="field-error" id={`${id}-${field}-error`}>
        {fieldErrors[field]}
      </p>
    );

  return (
    <form className="task-form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor={`${id}-title`}>Title</label>
        <input
          id={`${id}-title`}
          value={title}
          maxLength={200}
          onChange={(event) => setTitle(event.target.value)}
          aria-invalid={Boolean(fieldErrors.title)}
          aria-describedby={describedBy("title")}
        />
        {fieldError("title")}
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor={`${id}-due`}>Due (optional)</label>
          <input
            id={`${id}-due`}
            type="datetime-local"
            value={due}
            onChange={(event) => setDue(event.target.value)}
            aria-invalid={Boolean(fieldErrors.dueAt)}
            aria-describedby={describedBy("dueAt")}
          />
          {fieldError("dueAt")}
        </div>
        <div className="field">
          <label htmlFor={`${id}-minutes`}>Estimate in minutes (optional)</label>
          <input
            id={`${id}-minutes`}
            type="number"
            min={1}
            max={1440}
            value={minutes}
            onChange={(event) => setMinutes(event.target.value)}
            aria-invalid={Boolean(fieldErrors.estimatedMinutes)}
            aria-describedby={describedBy("estimatedMinutes")}
          />
          {fieldError("estimatedMinutes")}
        </div>
        <div className="field">
          <label htmlFor={`${id}-priority`}>Priority</label>
          <select
            id={`${id}-priority`}
            value={priority}
            onChange={(event) => setPriority(event.target.value as TaskPriority)}
          >
            {PRIORITIES.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <label className="check-field">
        <input
          type="checkbox"
          checked={isFixed}
          onChange={(event) => setIsFixed(event.target.checked)}
        />
        This happens at a fixed time, like a meeting
      </label>
      {isFixed ? (
        <div className="field-row">
          <div className="field">
            <label htmlFor={`${id}-fixed-start`}>Starts</label>
            <input
              id={`${id}-fixed-start`}
              type="datetime-local"
              value={fixedStart}
              onChange={(event) => setFixedStart(event.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor={`${id}-fixed-end`}>Ends</label>
            <input
              id={`${id}-fixed-end`}
              type="datetime-local"
              value={fixedEnd}
              onChange={(event) => setFixedEnd(event.target.value)}
              aria-invalid={Boolean(fieldErrors.fixedEndAt)}
              aria-describedby={describedBy("fixedEndAt")}
            />
            {fieldError("fixedEndAt")}
          </div>
        </div>
      ) : (
        <div className="field">
          <label htmlFor={`${id}-period`}>Preferred time of day (optional)</label>
          <select
            id={`${id}-period`}
            value={period}
            onChange={(event) => setPeriod(event.target.value)}
          >
            <option value="">Any time</option>
            <option value="morning">Morning</option>
            <option value="afternoon">Afternoon</option>
            <option value="evening">Evening</option>
          </select>
        </div>
      )}
      <div className="field">
        <label htmlFor={`${id}-description`}>Notes (optional)</label>
        <textarea
          id={`${id}-description`}
          rows={2}
          value={description}
          maxLength={5000}
          onChange={(event) => setDescription(event.target.value)}
          aria-invalid={Boolean(fieldErrors.description)}
          aria-describedby={describedBy("description")}
        />
        {fieldError("description")}
      </div>
      {formError && (
        <p className="message message-error" role="alert">
          {formError}
        </p>
      )}
      <div className="actions">
        <button type="submit" className="button-primary" disabled={saving}>
          {saving ? "Saving…" : submitLabel}
        </button>
        {onDiscard && (
          <button type="button" onClick={onDiscard} disabled={saving}>
            {discardLabel}
          </button>
        )}
      </div>
    </form>
  );
}
