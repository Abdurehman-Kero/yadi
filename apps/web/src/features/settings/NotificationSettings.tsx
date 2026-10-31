"use client";

import { useEffect, useState } from "react";
import {
  errorMessage,
  getServiceStatus,
  savePushSubscription,
  type ServiceStatus,
  removePushSubscription,
} from "@/lib/api";

type PushState = "checking" | "unsupported" | "off" | "denied" | "on";

function urlBase64ToBytes(value: string): Uint8Array<ArrayBuffer> {
  const padded = value + "=".repeat((4 - (value.length % 4)) % 4);
  const raw = atob(padded.replaceAll("-", "+").replaceAll("_", "/"));
  return Uint8Array.from(raw, (character) => character.charCodeAt(0));
}

function pushSupported(): boolean {
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

async function currentSubscription(): Promise<PushSubscription | null> {
  const registration = await navigator.serviceWorker.register("/sw.js");
  return registration.pushManager.getSubscription();
}

export function NotificationSettings() {
  const [status, setStatus] = useState<ServiceStatus | null>(null);
  const [push, setPush] = useState<PushState>("checking");
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

  useEffect(() => {
    let current = true;
    getServiceStatus()
      .then(async (loaded) => {
        let state: PushState = "off";
        if (!pushSupported()) state = "unsupported";
        else if (Notification.permission === "denied") state = "denied";
        else if (loaded.pushAvailable && (await currentSubscription())) state = "on";
        if (!current) return;
        setStatus(loaded);
        setPush(state);
      })
      .catch((failure) => {
        if (current) setError(errorMessage(failure));
      });
    return () => {
      current = false;
    };
  }, []);

  async function enable() {
    if (!status?.pushPublicKey) return;
    setWorking(true);
    setError(null);
    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setPush(permission === "denied" ? "denied" : "off");
        return;
      }
      const registration = await navigator.serviceWorker.register("/sw.js");
      await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToBytes(status.pushPublicKey),
      });
      const json = subscription.toJSON();
      await savePushSubscription({
        endpoint: subscription.endpoint,
        keys: { p256dh: json.keys?.p256dh ?? "", auth: json.keys?.auth ?? "" },
      });
      setPush("on");
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setWorking(false);
    }
  }

  async function disable() {
    setWorking(true);
    setError(null);
    try {
      const subscription = await currentSubscription();
      if (subscription) {
        await removePushSubscription(subscription.endpoint);
        await subscription.unsubscribe();
      }
      setPush("off");
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="notifications-settings">
      <h2 id="notifications-settings">Notifications</h2>
      <p role="status">
        {status === null
          ? "Checking the reminder service…"
          : status.running
            ? "Reminder service: running."
            : "Reminder service: not running. Reminders wait safely until it starts."}
      </p>
      <p className="hint">
        Reminders always appear in Notifications. Browser alerts can also reach you with Yadi
        closed, though your browser or device may silence them, and sound is not guaranteed.
      </p>
      {status && !status.pushAvailable && (
        <p className="hint">Browser alerts are not set up on this server.</p>
      )}
      {status?.pushAvailable && push === "unsupported" && (
        <p className="hint">This browser does not support alerts.</p>
      )}
      {status?.pushAvailable && push === "denied" && (
        <p className="hint">
          Alerts are blocked for this site. Allow them in your browser&apos;s site settings, then
          come back.
        </p>
      )}
      {status?.pushAvailable && push === "off" && (
        <div className="actions">
          <button type="button" className="button-primary" disabled={working} onClick={enable}>
            Turn on browser alerts
          </button>
        </div>
      )}
      {status?.pushAvailable && push === "on" && (
        <div className="actions">
          <span>Browser alerts are on.</span>
          <button type="button" disabled={working} onClick={disable}>
            Turn off browser alerts
          </button>
        </div>
      )}
      {error && (
        <p className="message message-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
