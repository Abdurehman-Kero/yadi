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

function respond(status: number, body: unknown) {
  return { ok: status < 400, status, json: async () => body };
}

function setup(onExtract: () => unknown) {
  const created = { ...draft, id: "1", title: "Saved" };
  const fetchMock = vi.fn(async (url: string) =>
    url.includes("/assistant/extract") ? onExtract() : respond(201, created),
  );
  vi.stubGlobal("fetch", fetchMock);
  const onCreated = vi.fn();
  render(<AssistantCapture timeZone="Africa/Addis_Ababa" onCreated={onCreated} />);
  return { fetchMock, onCreated };
}

function send(text: string) {
  fireEvent.change(screen.getByLabelText("Your message"), { target: { value: text } });
  fireEvent.click(screen.getByRole("button", { name: "Understand" }));
}

const taskCalls = (mock: ReturnType<typeof vi.fn>) =>
  mock.mock.calls.filter(([url]) => String(url).endsWith("/tasks"));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("AssistantCapture", () => {
  it("shows the draft for review and saves nothing until confirmed", async () => {
    const { fetchMock, onCreated } = setup(() => respond(200, { drafts: [draft], note: null }));
    send("finish my assignment");

    expect(await screen.findByLabelText("Title")).toHaveValue("Finish assignment");
    expect(screen.getByText("Which Tuesday?")).toBeInTheDocument();
    expect(screen.getByText(/I am unsure/)).toBeInTheDocument();
    expect(screen.getByText(/You said “Tuesday at 10”/)).toHaveTextContent("10:00");
    expect(screen.getByLabelText(/Estimate/)).toHaveValue(120);
    expect(taskCalls(fetchMock)).toHaveLength(0);

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Corrected title" } });
    fireEvent.click(screen.getByRole("button", { name: "Save task" }));
    await waitFor(() => expect(onCreated).toHaveBeenCalledOnce());
    const body = JSON.parse(taskCalls(fetchMock)[0][1].body);
    expect(body.title).toBe("Corrected title");
    expect(body.priority).toBe("high");
    expect(body.dueAt).toBe("2030-01-15T07:00:00.000Z");
    expect(screen.queryByLabelText("Title")).not.toBeInTheDocument();
  });

  it("discarding a draft saves nothing", async () => {
    const { fetchMock } = setup(() => respond(200, { drafts: [draft], note: null }));
    send("x");
    fireEvent.click(await screen.findByRole("button", { name: "Discard" }));
    expect(screen.queryByLabelText("Title")).not.toBeInTheDocument();
    expect(taskCalls(fetchMock)).toHaveLength(0);
  });

  it("opens the manual form with the text kept when the AI fails", async () => {
    setup(() =>
      respond(503, { error: { code: "AI_UNAVAILABLE", message: "AI is not available." } }),
    );
    send("call my advisor");
    expect(await screen.findByRole("alert")).toHaveTextContent("AI is not available.");
    expect(screen.getByLabelText("Title")).toHaveValue("call my advisor");
    expect(screen.getByLabelText("Your message")).toHaveValue("call my advisor");
  });

  it("shows the assistant's note when there is nothing to save", async () => {
    setup(() => respond(200, { drafts: [], note: "I can only record that as a task." }));
    send("send an email");
    expect(await screen.findByText("I can only record that as a task.")).toBeInTheDocument();
    expect(screen.getByLabelText("Your message")).toHaveValue("send an email");
  });
});
