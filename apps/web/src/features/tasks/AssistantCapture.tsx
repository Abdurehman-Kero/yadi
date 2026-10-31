"use client";

import { type FormEvent, useRef, useState } from "react";
import { Modal } from "@/components/Modal";
import {
  applyAssistantAction,
  createTask,
  errorMessage,
  extractTasks,
  sendAssistantMessage,
  type AssistantReply,
  type ProposedAction,
  type Task,
  type TaskCreate,
  type TaskDraft,
} from "@/lib/api";
import { formatDateTime } from "@/lib/time";
import { TaskForm } from "./TaskForm";

type Props = {
  timeZone: string;
  onCreated: (task: Task) => void;
  /** Called after the assistant changed something, so the page can show the new state. */
  onChanged?: () => void;
};
type ReviewItem = { key: number; draft: TaskDraft };
type Turn = { key: number; role: "user" | "assistant"; text: string };

const FALLBACK_TITLE_LENGTH = 200;
// The conversation lives only in this page: it is not stored, and a reload clears it.
const MAX_TURNS_SENT = 6;
const MAX_TURN_LENGTH = 500;

export function AssistantCapture({ timeZone, onCreated, onChanged }: Props) {
  const [text, setText] = useState("");
  const [working, setWorking] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [pending, setPending] = useState<AssistantReply | null>(null);
  const [recentTaskIds, setRecentTaskIds] = useState<string[]>([]);
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [failure, setFailure] = useState<string | null>(null);
  const [manual, setManual] = useState<Partial<TaskCreate> | null>(null);
  const nextKey = useRef(0);

  function say(role: Turn["role"], message: string) {
    setTurns((list) => [...list, { key: nextKey.current++, role, text: message }]);
  }

  function handleReply(reply: AssistantReply) {
    say("assistant", reply.message);
    if (reply.taskIds.length > 0) setRecentTaskIds(reply.taskIds.slice(0, 5));
    setPending(reply.kind === "confirm" || reply.kind === "choose" ? reply : null);
    if (reply.kind === "done") onChanged?.();
  }

  async function capture(message: string) {
    const result = await extractTasks(message);
    setItems(result.drafts.map((draft) => ({ key: nextKey.current++, draft })));
    if (result.drafts.length === 0) {
      say("assistant", result.note ?? "I did not find a task in that. Try rewording it.");
    } else if (result.note) {
      say("assistant", result.note);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const message = text.trim();
    if (!message) return;
    setWorking(true);
    setFailure(null);
    setManual(null);
    setItems([]);
    setPending(null);
    const history = turns
      .slice(-MAX_TURNS_SENT)
      .map((turn) => ({ role: turn.role, text: turn.text.slice(0, MAX_TURN_LENGTH) }));
    say("user", message);
    try {
      const reply = await sendAssistantMessage(message, history, recentTaskIds);
      if (reply.kind === "create_tasks") {
        await capture(message);
      } else {
        handleReply(reply);
        setText("");
      }
    } catch (error) {
      setFailure(errorMessage(error));
      setManual({ title: message.slice(0, FALLBACK_TITLE_LENGTH), priority: "medium" });
    } finally {
      setWorking(false);
    }
  }

  async function apply(action: ProposedAction, confirmed: boolean) {
    setWorking(true);
    setFailure(null);
    setPending(null);
    try {
      handleReply(await applyAssistantAction(action, confirmed));
    } catch (error) {
      setFailure(errorMessage(error));
    } finally {
      setWorking(false);
    }
  }

  function remove(key: number) {
    setItems((list) => list.filter((item) => item.key !== key));
  }

  function saved(key: number, task: Task) {
    onCreated(task);
    remove(key);
    say("assistant", `Added "${task.title}".`);
    setRecentTaskIds([task.id]);
    // The message has done its job once something from it is saved.
    setText("");
  }

  return (
    <section aria-labelledby="tell-yadi" className="panel">
      <h2 id="tell-yadi">Tell Yadi</h2>

      {turns.length > 0 && (
        <div className="thread" aria-label="Conversation" role="log" tabIndex={0}>
          <ol className="thread-list">
            {turns.map((turn) => (
              <li className={`turn turn-${turn.role}`} key={turn.key}>
                <span className="visually-hidden">
                  {turn.role === "user" ? "You said: " : "Yadi said: "}
                </span>
                {turn.text}
              </li>
            ))}
          </ol>
        </div>
      )}

      {pending?.kind === "choose" && pending.action && (
        <ul className="option-list" aria-label="Choose a task">
          {pending.options.map((option) => (
            <li key={option.taskId}>
              <button
                type="button"
                className="option"
                disabled={working}
                onClick={() =>
                  apply({ ...(pending.action as ProposedAction), taskId: option.taskId }, false)
                }
              >
                <strong>{option.title}</strong>
                <span className="hint">{option.detail}</span>
              </button>
            </li>
          ))}
          <li>
            <button
              type="button"
              className="button-quiet"
              disabled={working}
              onClick={() => setPending(null)}
            >
              None of these
            </button>
          </li>
        </ul>
      )}

      {pending?.kind === "confirm" && pending.action && (
        <div className="actions">
          <button
            type="button"
            className="button-primary"
            disabled={working}
            onClick={() => apply(pending.action as ProposedAction, true)}
          >
            Yes, do it
          </button>
          <button
            type="button"
            disabled={working}
            onClick={() => {
              setPending(null);
              say("assistant", "Okay, I did not change anything.");
            }}
          >
            No, keep it
          </button>
        </div>
      )}

      <form className="composer" onSubmit={handleSubmit}>
        <label htmlFor="assistant-text" className="visually-hidden">
          Your message
        </label>
        <textarea
          id="assistant-text"
          rows={1}
          maxLength={2000}
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => {
            // Enter sends, as in any chat. Shift+Enter still makes a new line.
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Assignment due Friday at 5 PM, or: move my project to the afternoon"
        />
        <button type="submit" className="button-primary" disabled={working || !text.trim()}>
          {working ? "Working…" : "Send"}
        </button>
      </form>
      <p className="hint">
        Sent to Google Gemini to be understood. Yadi asks before anything hard to undo.
      </p>

      <p className="visually-hidden" role="status">
        {working ? "Yadi is reading your message…" : ""}
      </p>
      {failure && !manual && (
        <p className="message message-error" role="alert">
          {failure}
        </p>
      )}

      {manual && (
        <Modal title="Add it yourself" onClose={() => setManual(null)}>
          {failure && (
            <p className="message message-error" role="alert">
              {failure}
            </p>
          )}
          <p className="hint">
            If you meant to change something, you can do that from Tasks or Schedule instead.
          </p>
          <TaskForm
            initial={manual}
            timeZone={timeZone}
            submitLabel="Save task"
            onSubmit={async (values) => {
              onCreated(await createTask(values));
              setManual(null);
              setFailure(null);
              setText("");
            }}
          />
        </Modal>
      )}

      {items.length > 0 && (
        <Modal title="Check what I understood" onClose={() => setItems([])}>
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
                onSubmit={async (values) => saved(key, await createTask(values))}
              />
            </div>
          ))}
        </Modal>
      )}
    </section>
  );
}
