import "@testing-library/jest-dom/vitest";

// jsdom has no modal behaviour for <dialog>; these give it the same open attribute.
HTMLDialogElement.prototype.showModal = function showModal() {
  this.setAttribute("open", "");
};
HTMLDialogElement.prototype.close = function close() {
  this.removeAttribute("open");
};
