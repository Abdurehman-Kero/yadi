"use client";

import { type FormEvent, useRef, useState } from "react";
import {
  createTask,
  errorMessage,
  extractTasks,
  type Task,
  type TaskCreate,
  type TaskDraft,
} from "@/lib/api";
import { formatDateTime } from "@/lib/time";
import { TaskForm } from "./TaskForm";

type Props = { timeZone: string; onCreated: (task: Task) => void };
type ReviewItem = { key: number; draft: TaskDraft };

const FALLBACK_TITLE_LENGTH = 200;

export function AssistantCapture({ timeZone, onCreated }: Props) {
  const [text, setText] = useState("");
  const [working, setWorking] = useState(false);
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [failure, setFailure] = useState<string | null>(null);
  const [manual, setManual] = useState<TaskCreate | null>(null);
  const nextKey = useRef(0);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const message = text.trim();
    if (!message) return;
    setWorking(true);
    setFailure(null);
    setManual(null);
    setNote(null);
    setItems([]);
    try {
      const result = await extractTasks(message);
      setItems(result.drafts.map((draft) => ({ key: nextKey.current++, draft })));
      setNote(
        result.note ??
          (result.drafts.length === 0 ? "I did not find a task in that. Try rewording it." : null),
      );
      if (result.drafts.length > 0) setText("");
    } catch (error) {
      setFailure(errorMessage(error));
      setManual({ title: message.slice(0, FALLBACK_TITLE_LENGTH), priority: "medium" });
    } finally {
      setWorking(false);
    }
  }

  function remove(key: number) {
    setItems((list) => list.filter((item) => item.key !== key));
  }

  return (
    <section aria-labelledby="tell-yadi" className="panel">
      <h2 id="tell-yadi">Tell Yadi what you need to do</h2>
      <form className="task-form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="assistant-text">Your message</label>
          <textarea
            id="assistant-text"
            rows={2}
            maxLength={2000}
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="I have an assignment due Friday at 5 PM, and I need two hours for my project."
          />
        </div>
        <div className="actions">
          <button type="submit" className="button-primary" disabled={working || !text.trim()}>
            {working ? "Understanding…" : "Understand"}
          </button>
        </div>
        <p className="hint">
          Your message goes to Google Gemini, our AI provider, to be understood. You review
          everything before it is saved.
        </p>
      </form>

      <p className="live-region" role="status">
        {working ? "Yadi is reading your message…" : note}
      </p>

      {failure && (
        <p className="message message-error" role="alert">
          {failure}
        </p>
      )}
      {manual && (
        <div className="review-item">
          <h3>Add it yourself</h3>
          <TaskForm
            initial={manual}
            timeZone={timeZone}
            submitLabel="Save task"
            onDiscard={() => setManual(null)}
            onSubmit={async (values) => {
              onCreated(await createTask(values));
              setManual(null);
              setFailure(null);
              setText("");
            }}
          />
        </div>
      )}

      {items.length > 0 && <h3>Check what I understood</h3>}
      {items.map(({ key, draft }, index) => (
        <div className="review-item" key={key}>
          <p className="review-label">
            Task {index + 1}
            {draft.confidence === "low" && " · I am unsure about this one"}
          </p>
          {draft.duePhrase && (
            <p className="hint">
              You said &ldquo;{draft.duePhrase}&rdquo;
              {draft.dueAt && `, which I read as ${formatDateTime(draft.dueAt, timeZone)}`}.
            </p>
          )}
          {draft.questions.length > 0 && (
            <ul className="questions">
              {draft.questions.map((question) => (
                <li key={`${question.field}-${question.question}`}>{question.question}</li>
              ))}
            </ul>
          )}
          <TaskForm
            initial={draft}
            timeZone={timeZone}
            submitLabel="Save task"
            discardLabel="Discard"
            onDiscard={() => remove(key)}
            onSubmit={async (values) => {
              onCreated(await createTask(values));
              remove(key);
            }}
          />
        </div>
      ))}
    </section>
  );
}
