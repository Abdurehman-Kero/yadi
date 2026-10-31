"use client";

import { useEffect, useState } from "react";
import { listNotifications } from "@/lib/api";

export const NOTIFICATIONS_CHANGED = "yadi:notifications-changed";
const REFRESH_MS = 30_000;

/** Unread count for the navigation. Pauses while the tab is hidden, to avoid needless requests. */
export function useUnreadCount(): number {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let current = true;
    const refresh = () => {
      listNotifications()
        .then((list) => {
          if (current) setCount(list.unread);
        })
        // The badge is secondary: a failure here must not disturb the page, which reports its own.
        .catch(() => {});
    };
    const refreshIfVisible = () => {
      if (document.visibilityState === "visible") refresh();
    };
    refresh();
    const timer = setInterval(refreshIfVisible, REFRESH_MS);
    window.addEventListener(NOTIFICATIONS_CHANGED, refresh);
    document.addEventListener("visibilitychange", refreshIfVisible);
    return () => {
      current = false;
      clearInterval(timer);
      window.removeEventListener(NOTIFICATIONS_CHANGED, refresh);
      document.removeEventListener("visibilitychange", refreshIfVisible);
    };
  }, []);

  return count;
}
