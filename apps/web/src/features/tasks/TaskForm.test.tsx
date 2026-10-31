import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { TaskForm } from "./TaskForm";

afterEach(cleanup);

function setup(onSubmit = vi.fn().mockResolvedValue(undefined)) {
  render(<TaskForm timeZone="Africa/Addis_Ababa" submitLabel="Add task" onSubmit={onSubmit} />);
  return onSubmit;
}

const submit = () => fireEvent.click(screen.getByRole("button", { name: "Add task" }));
const typeTitle = (value: string) =>
  fireEvent.change(screen.getByLabelText("Title"), { target: { value } });

describe("TaskForm", () => {
  it("requires a title without calling the server", () => {
    const onSubmit = setup();
    submit();
    expect(screen.getByText("Enter a title.")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("sends the due time converted from the user's timezone, and clears after success", async () => {
    const onSubmit = setup();
    typeTitle("Report");
    fireEvent.change(screen.getByLabelText("Due (optional)"), {
      target: { value: "2030-01-15T10:00" },
    });
    submit();
    await waitFor(() => expect(screen.getByLabelText("Title")).toHaveValue(""));
    expect(onSubmit).toHaveBeenCalledWith({
      title: "Report",
      description: null,
      priority: "medium",
      dueAt: "2030-01-15T07:00:00.000Z",
      estimatedMinutes: null,
      fixedStartAt: null,
      fixedEndAt: null,
      preferredPeriod: null,
      reminderEnabled: true,
      reminderMinutesBefore: null,
    });
  });

  it("sends the chosen reminder", async () => {
    const onSubmit = setup();
    typeTitle("Report");
    fireEvent.change(screen.getByLabelText("Reminder"), { target: { value: "none" } });
    submit();
    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      reminderEnabled: false,
      reminderMinutesBefore: null,
    });
  });

  it("keeps the input and shows the server's field error", async () => {
    setup(
      vi
        .fn()
        .mockRejectedValue(
          new ApiError("VALIDATION_FAILED", "Invalid request.", [
            { field: "estimatedMinutes", issue: "Must be at most 1440." },
          ]),
        ),
    );
    typeTitle("Report");
    submit();
    expect(await screen.findByText("Must be at most 1440.")).toBeInTheDocument();
    expect(screen.getByLabelText("Title")).toHaveValue("Report");
    expect(screen.getByLabelText(/Estimate/)).toHaveAttribute("aria-invalid", "true");
  });

  it("sends a fixed time and requires both ends of it", async () => {
    const onSubmit = setup();
    typeTitle("Meeting");
    fireEvent.click(screen.getByLabelText(/fixed time/));
    submit();
    expect(screen.getByText("Enter both a start and an end.")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();

    fireEvent.change(screen.getByLabelText("Starts"), { target: { value: "2030-01-15T10:00" } });
    fireEvent.change(screen.getByLabelText("Ends"), { target: { value: "2030-01-15T11:00" } });
    submit();
    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      fixedStartAt: "2030-01-15T07:00:00.000Z",
      fixedEndAt: "2030-01-15T08:00:00.000Z",
      preferredPeriod: null,
    });
  });

  it("keeps the input and shows a message when the server is unreachable", async () => {
    setup(vi.fn().mockRejectedValue(new ApiError("NETWORK", "Could not reach Yadi.")));
    typeTitle("Report");
    submit();
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not reach Yadi.");
    expect(screen.getByLabelText("Title")).toHaveValue("Report");
  });
});
