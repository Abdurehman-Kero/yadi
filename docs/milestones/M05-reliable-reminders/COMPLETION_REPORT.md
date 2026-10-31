# M05 Completion Report

**Status: BUILT AND VERIFIED, except real browser alerts; awaiting owner review.** (2026-10-31 UTC). Not committed: the owner makes commits.

## Delivered
- Migration 0005; reminders that follow the task; worker process with leases, retries, recovery and heartbeat.
- In-app notifications with unread badge, snooze and read state; reminder choice per task; reminder-service status.
- Web Push channel, service worker, permission flow, key-generation script.
- Modal dialogs: new task, edit task, move block, cancel confirmation, Tell Yadi review and fallback.

## Verified
- `node scripts/run.mjs all`: 10/10 PASS. pytest 178, vitest 23, Playwright 22.
- A real worker process was killed; work that fell due while it was down was delivered exactly once after restart. Nothing used a browser.
- Four concurrent workers on 30 due reminders produced exactly 30 notifications.
- Retry schedule, final failure, expired leases, late reminders and finished tasks tested with an injected clock.
- Timeliness: delivery delay p95 about 2 s with a 1 s poll, over 20 reminders on this machine. The production default poll is 5 s, which should add up to 4 s; that default was not measured separately. Not a load test.
- Browser test: the real worker's reminder appeared in the UI; snooze worked.
- Modals: focus stays inside, Escape closes, focus returns to the opener; axe finds no serious issue with a modal open, or on any screen, in light and dark mode.
- Push encryption and VAPID signing tested with the real library and real keys; only the final HTTP call was replaced. Expired subscriptions are removed. Push failure does not undo or repeat delivery.
- `npm audit --omit=dev` and `pip-audit`: no known vulnerabilities.

## Bugs found and fixed during the build
- Push key field would have been renamed `p256Dh` by the API's naming rule, so real browsers' subscriptions would have been rejected (type checker).
- Focus did not return to the opener after a modal closed (browser test).
- Browser tests picked up real keys from `.env`; the test configuration now blanks them.

## Not verified / limitations
- **A real alert has never reached a real browser.** Headless test browsers cannot receive push. Needs the owner's manual check; see DEMO_SCRIPT.
- The demo script was not run by hand end to end.
- The worker must be running for anything to send. Without it, reminders wait safely and Settings and Notifications say so. Nothing restarts it automatically; hosting must supply that.
- Push failures are recorded but not retried; the in-app notification is the guarantee.
- A crash between committing the in-app notification and sending push loses that push only.
- Changing the default lead time applies to tasks when they next change or are replanned, not immediately.
- Recurring reminders, email and sound are not included. Sound is never promised.
- Still development identity only: do not host (D-015).

## Deviations
- Late reminders are delivered with honest wording rather than cancelled (see PLAN.md).
- Real sign-in moved out of M05, at the owner's approval (D-015). ADR-005 is updated.
