import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AssistantCapture } from "./AssistantCapture";

const draft = {
  title: "Finish assignment",
  description: null,
  dueAt: "2030-01-15T07:00:00Z",
  duePhrase: "Tuesday at 10",
  estimatedMinutes: 120,
  priority: "high",
  confidence: "low",
  questions: [{ field: "due", question: "Which Tuesday?" }],
};
const CREATE = { kind: "create_tasks", message: "x", options: [], taskIds: [] };

function respond(status: number, body: unknown) {
  return { ok: status < 400, status, json: async () => body };
}

type Handlers = {
  message?: () => unknown;
  extract?: () => unknown;
  apply?: () => unknown;
};

function setup(handlers: Handlers) {
  const created = { ...draft, id: "1", title: "Saved" };
  const fetchMock = vi.fn(async (url: string) => {
    if (url.includes("/assistant/message")) {
      return handlers.message ? handlers.message() : respond(200, CREATE);
    }
    if (url.includes("/assistant/extract")) return handlers.extract?.();
    if (url.includes("/assistant/apply")) return handlers.apply?.();
    return respond(201, created);
  });
  vi.stubGlobal("fetch", fetchMock);
  const onCreated = vi.fn();
  const onChanged = vi.fn();
  render(
    <AssistantCapture timeZone="Africa/Addis_Ababa" onCreated={onCreated} onChanged={onChanged} />,
  );
  return { fetchMock, onCreated, onChanged };
}

function send(text: string) {
  fireEvent.change(screen.getByLabelText("Your message"), { target: { value: text } });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
}

const taskCalls = (mock: ReturnType<typeof vi.fn>) =>
  mock.mock.calls.filter(([url]) => String(url).endsWith("/tasks"));
const callsTo = (mock: ReturnType<typeof vi.fn>, part: string) =>
  mock.mock.calls.filter(([url]) => String(url).includes(part));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("capturing new tasks", () => {
  it("shows the draft for review and saves nothing until confirmed", async () => {
    const { fetchMock, onCreated } = setup({
      extract: () => respond(200, { drafts: [draft], note: null }),
    });
    send("finish my assignment");

    expect(await screen.findByLabelText("Title")).toHaveValue("Finish assignment");
    expect(screen.getByText("Which Tuesday?")).toBeInTheDocument();
    expect(screen.getByText(/I am unsure/)).toBeInTheDocument();
    expect(screen.getByText(/You said “Tuesday at 10”/)).toHaveTextContent("10:00");
    expect(taskCalls(fetchMock)).toHaveLength(0);

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Corrected title" } });
    fireEvent.click(screen.getByRole("button", { name: "Save task" }));
    await waitFor(() => expect(onCreated).toHaveBeenCalledOnce());
    const body = JSON.parse(taskCalls(fetchMock)[0][1].body);
    expect(body.title).toBe("Corrected title");
    expect(body.dueAt).toBe("2030-01-15T07:00:00.000Z");
    expect(screen.queryByLabelText("Title")).not.toBeInTheDocument();
  });

  it("discarding a draft saves nothing", async () => {
    const { fetchMock } = setup({ extract: () => respond(200, { drafts: [draft], note: null }) });
    send("x");
    fireEvent.click(await screen.findByRole("button", { name: "Discard" }));
    expect(screen.queryByLabelText("Title")).not.toBeInTheDocument();
    expect(taskCalls(fetchMock)).toHaveLength(0);
  });

  it("opens the manual form with the text kept when the AI fails", async () => {
    setup({
      message: () =>
        respond(503, { error: { code: "AI_UNAVAILABLE", message: "AI is not available." } }),
    });
    send("call my advisor");
    expect(await screen.findByRole("alert")).toHaveTextContent("AI is not available.");
    expect(screen.getByLabelText("Title")).toHaveValue("call my advisor");
    expect(screen.getByLabelText("Your message")).toHaveValue("call my advisor");
  });
});

describe("changing the plan by message", () => {
  it("shows the result and refreshes the page after a change", async () => {
    const { onChanged } = setup({
      message: () =>
        respond(200, {
          kind: "done",
          message: 'Moved "Report" to Mon, 14:00.',
          options: [],
          taskIds: ["t1"],
        }),
    });
    send("move the report");
    expect(await screen.findByText('Moved "Report" to Mon, 14:00.')).toBeInTheDocument();
    expect(onChanged).toHaveBeenCalledOnce();
    expect(screen.getByLabelText("Your message")).toHaveValue("");
  });

  it("only refreshes when something changed", async () => {
    const { onChanged } = setup({
      message: () =>
        respond(200, { kind: "answer", message: "Next is X.", options: [], taskIds: [] }),
    });
    send("what next?");
    expect(await screen.findByText("Next is X.")).toBeInTheDocument();
    expect(onChanged).not.toHaveBeenCalled();
  });

  it("asks which task, and sends the chosen one", async () => {
    const action = { kind: "complete" };
    const { fetchMock, onChanged } = setup({
      message: () =>
        respond(200, {
          kind: "choose",
          message: "Which one do you mean?",
          action,
          options: [
            { taskId: "a", title: "Report A", detail: "Inbox" },
            { taskId: "b", title: "Report B", detail: "Inbox" },
          ],
          taskIds: [],
        }),
      apply: () => respond(200, { kind: "done", message: "Done.", options: [], taskIds: ["b"] }),
    });
    send("report is done");
    fireEvent.click(await screen.findByRole("button", { name: /Report B/ }));
    await screen.findByText("Done.");
    const body = JSON.parse(callsTo(fetchMock, "/assistant/apply")[0][1].body);
    expect(body).toEqual({ action: { kind: "complete", taskId: "b" }, confirmed: false });
    expect(onChanged).toHaveBeenCalledOnce();
    expect(screen.queryByRole("button", { name: /Report A/ })).not.toBeInTheDocument();
  });

  it("changes nothing until confirmed, and declining sends nothing", async () => {
    const confirm = {
      kind: "confirm",
      message: 'Cancel "Report"?',
      action: { kind: "cancel", taskId: "t1" },
      options: [],
      taskIds: ["t1"],
    };
    const { fetchMock, onChanged } = setup({
      message: () => respond(200, confirm),
      apply: () => respond(200, { kind: "done", message: "Cancelled.", options: [], taskIds: [] }),
    });
    send("cancel the report");
    fireEvent.click(await screen.findByRole("button", { name: "No, keep it" }));
    expect(screen.getByText("Okay, I did not change anything.")).toBeInTheDocument();
    expect(callsTo(fetchMock, "/assistant/apply")).toHaveLength(0);
    expect(onChanged).not.toHaveBeenCalled();

    send("cancel the report");
    fireEvent.click(await screen.findByRole("button", { name: "Yes, do it" }));
    await screen.findByText("Cancelled.");
    const body = JSON.parse(callsTo(fetchMock, "/assistant/apply")[0][1].body);
    expect(body.confirmed).toBe(true);
    expect(onChanged).toHaveBeenCalledOnce();
  });

  it("sends earlier turns and the task just discussed with the next message", async () => {
    const { fetchMock } = setup({
      message: () =>
        respond(200, { kind: "answer", message: "Next is X.", options: [], taskIds: ["t9"] }),
    });
    send("what next?");
    await screen.findByText("Next is X.");
    send("I finished it");
    await waitFor(() => expect(callsTo(fetchMock, "/assistant/message")).toHaveLength(2));
    const body = JSON.parse(callsTo(fetchMock, "/assistant/message")[1][1].body);
    expect(body.text).toBe("I finished it");
    expect(body.recentTaskIds).toEqual(["t9"]);
    expect(body.history).toEqual([
      { role: "user", text: "what next?" },
      { role: "assistant", text: "Next is X." },
    ]);
  });
});
