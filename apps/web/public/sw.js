// Receives reminders while Yadi is closed. The tag makes a repeat replace, not duplicate, an alert.
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(data.title ?? "Yadi", {
      body: data.body,
      tag: data.tag,
      data: { url: "/notifications" },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow(event.notification.data?.url ?? "/"));
});
