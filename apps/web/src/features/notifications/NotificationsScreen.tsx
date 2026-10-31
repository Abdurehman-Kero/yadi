"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  errorMessage,
  getPreferences,
  getServiceStatus,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  snoozeReminder,
  type NotificationList,
  type ServiceStatus,
} from "@/lib/api";
import { formatDateTime } from "@/lib/time";
import { NOTIFICATIONS_CHANGED } from "./useUnreadCount";

const REFRESH_MS = 30_000;
const SNOOZES = [
  { minutes: 10, label: "10 min" },
  { minutes: 60, label: "1 hour" },
];

type Data = { list: NotificationList; status: ServiceStatus; timeZone: string };

export function NotificationsScreen() {
  const [data, setData] = useState<Data | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [list, status, preferences] = await Promise.all([
        listNotifications(),
        getServiceStatus(),
        getPreferences(),
      ]);
      setData({ list, status, timeZone: preferences.timezone });
      setLoadError(null);
    } catch (error) {
      setLoadError(errorMessage(error));
    }
    window.dispatchEvent(new Event(NOTIFICATIONS_CHANGED));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Loading from the server on mount.
    void load();
    const timer = setInterval(() => {
      if (document.visibilityState === "visible") void load();
    }, REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  async function act(action: () => Promise<unknown>, done: string) {
    setActionError(null);
    setNotice(null);
    try {
      await action();
      setNotice(done);
      await load();
    } catch (error) {
      setActionError(errorMessage(error));
    }
  }

  const header = (
    <header className="page-header">
      <div>
        <h1>Notifications</h1>
        <p className="page-subtitle">Reminders Yadi has sent you.</p>
      </div>
      {data && data.list.unread > 0 && (
        <button type="button" onClick={() => act(markAllNotificationsRead, "All marked as read.")}>
          Mark all as read
        </button>
      )}
    </header>
  );

  if (loadError && !data) {
    return (
      <>
        {header}
        <div className="message message-error" role="alert">
          <p>{loadError}</p>
          <button type="button" onClick={() => void load()}>
            Try again
          </button>
        </div>
      </>
    );
  }
  if (!data) {
    return (
      <>
        {header}
        <p role="status">Loading your notifications…</p>
      </>
    );
  }

  return (
    <>
      {header}
      <p className="live-region" role="status">
        {notice}
      </p>
      {actionError && (
        <p className="message message-error" role="alert">
          {actionError}
        </p>
      )}
      {!data.status.running && (
        <p className="message message-warning">
          The reminder service is not running, so reminders are waiting. Nothing is lost: they will
          arrive, marked late if needed, once it starts. See <Link href="/settings">Settings</Link>.
        </p>
      )}
      <section className="panel" aria-label="Your notifications">
        {data.list.items.length === 0 ? (
          <p className="empty">
            Nothing yet. Tasks with a time get a reminder here, based on your{" "}
            <Link href="/settings">reminder settings</Link>.
          </p>
        ) : (
          <ul className="task-list">
            {data.list.items.map((item) => (
              <li className="task-row" key={item.id}>
                <div className="task-main">
                  <h2 className="task-title">
                    {item.readAt === null && <span className="badge badge-fixed">New</span>}{" "}
                    {item.title}
                  </h2>
                  <p className="task-notes">{item.body}</p>
                  <p className="task-meta">Sent {formatDateTime(item.createdAt, data.timeZone)}</p>
                </div>
                <div className="actions">
                  {SNOOZES.map((snooze) => (
                    <button
                      type="button"
                      key={snooze.minutes}
                      onClick={() =>
                        act(async () => {
                          await snoozeReminder(item.reminderId, snooze.minutes);
                          await markNotificationRead(item.id);
                        }, `Snoozed "${item.title}" for ${snooze.label}.`)
                      }
                    >
                      Snooze {snooze.label}
                      <span className="visually-hidden"> {item.title}</span>
                    </button>
                  ))}
                  <Link className="button-link" href="/schedule">
                    Reschedule
                  </Link>
                  {item.readAt === null && (
                    <button
                      type="button"
                      className="button-quiet"
                      onClick={() => act(() => markNotificationRead(item.id), "Marked as read.")}
                    >
                      Mark as read<span className="visually-hidden"> {item.title}</span>
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
