import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Modal } from "./Modal";

afterEach(cleanup);

describe("Modal", () => {
  it("opens labelled by its title and closes from the button", () => {
    const onClose = vi.fn();
    render(
      <Modal title="Edit task" onClose={onClose}>
        <p>Body</p>
      </Modal>,
    );
    expect(screen.getByRole("dialog", { name: "Edit task" })).toHaveAttribute("open");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("sends Escape through the parent instead of closing by itself", () => {
    const onClose = vi.fn();
    render(
      <Modal title="Edit task" onClose={onClose}>
        <p>Body</p>
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    fireEvent(dialog, new Event("cancel", { cancelable: true }));
    expect(onClose).toHaveBeenCalledOnce();
    expect(dialog).toHaveAttribute("open");
  });
});
