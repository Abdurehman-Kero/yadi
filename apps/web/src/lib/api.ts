import type { components } from "@/api/schema";

export type Task = components["schemas"]["TaskOut"];
export type TaskCreate = components["schemas"]["TaskCreate"];
export type TaskUpdate = components["schemas"]["TaskUpdate"];
export type TaskPage = components["schemas"]["TaskPage"];
export type TaskEvent = components["schemas"]["TaskEventOut"];
export type TaskStatus = Task["status"];
export type TaskPriority = Task["priority"];
export type Preferences = components["schemas"]["PreferencesModel"];

export type TaskDraft = components["schemas"]["TaskDraft"];
export type ExtractResponse = components["schemas"]["ExtractResponse"];

export type Schedule = components["schemas"]["ScheduleOut"];
export type ScheduleBlock = components["schemas"]["BlockOut"];
export type BlockUpdate = components["schemas"]["BlockUpdate"];

export type NotificationList = components["schemas"]["NotificationList"];
export type ServiceStatus = components["schemas"]["ServiceStatus"];
export type PushSubscriptionInput = components["schemas"]["SubscriptionRequest"];

export type AssistantReply = components["schemas"]["AssistantReply"];
export type ProposedAction = components["schemas"]["ProposedAction"];
export type ConversationTurn = components["schemas"]["Turn"];

export type ErrorDetail = { field: string; issue: string };

export class ApiError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly details: ErrorDetail[] = [],
  ) {
    super(message);
  }
}

const UNREACHABLE = "Could not reach Yadi. Check that the server is running, then try again.";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/v1${path}`, {
      ...init,
      headers: init?.body ? { "Content-Type": "application/json" } : undefined,
    });
  } catch {
    throw new ApiError("NETWORK", UNREACHABLE);
  }
  if (response.status === 204) return undefined as T;
  // A proxy failure while the API is down has no JSON body, so parsing must not be assumed.
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = body?.error;
    throw new ApiError(error?.code ?? "UNKNOWN", error?.message ?? UNREACHABLE, error?.details);
  }
  return body as T;
}

const send = <T>(method: string, path: string, data?: unknown) =>
  request<T>(path, { method, body: data === undefined ? undefined : JSON.stringify(data) });

export function listTasks(statuses: TaskStatus[], cursor?: string | null): Promise<TaskPage> {
  const params = new URLSearchParams({ limit: "50" });
  statuses.forEach((status) => params.append("status", status));
  if (cursor) params.set("cursor", cursor);
  return request(`/tasks?${params}`);
}

export const createTask = (data: TaskCreate) => send<Task>("POST", "/tasks", data);
export const updateTask = (id: string, data: TaskUpdate) =>
  send<Task>("PATCH", `/tasks/${id}`, data);
export const startTask = (id: string) => send<Task>("POST", `/tasks/${id}/start`);
export const completeTask = (id: string) => send<Task>("POST", `/tasks/${id}/complete`);
export const reopenTask = (id: string) => send<Task>("POST", `/tasks/${id}/reopen`);
export const cancelTask = (id: string) => send<Task>("DELETE", `/tasks/${id}`);
export const listTaskEvents = (id: string) => request<TaskEvent[]>(`/tasks/${id}/events`);

export const extractTasks = (text: string) =>
  send<ExtractResponse>("POST", "/assistant/extract", { text });

export const sendAssistantMessage = (
  text: string,
  history: ConversationTurn[],
  recentTaskIds: string[],
) => send<AssistantReply>("POST", "/assistant/message", { text, history, recentTaskIds });
export const applyAssistantAction = (action: ProposedAction, confirmed: boolean) =>
  send<AssistantReply>("POST", "/assistant/apply", { action, confirmed });

export const getSchedule = () => request<Schedule>("/schedule");
export const generateSchedule = () => send<Schedule>("POST", "/schedule/generate", { days: 7 });
export const updateBlock = (id: string, data: BlockUpdate) =>
  send<ScheduleBlock>("PATCH", `/schedule/blocks/${id}`, data);

export const listNotifications = () => request<NotificationList>("/notifications");
export const markNotificationRead = (id: string) =>
  send<unknown>("POST", `/notifications/${id}/read`);
export const markAllNotificationsRead = () => send<void>("POST", "/notifications/read-all");
export const snoozeReminder = (id: string, minutes: number) =>
  send<unknown>("POST", `/reminders/${id}/snooze`, { minutes });
export const getServiceStatus = () => request<ServiceStatus>("/reminders/service-status");
export const savePushSubscription = (data: PushSubscriptionInput) =>
  send<void>("POST", "/push/subscriptions", data);
export const removePushSubscription = (endpoint: string) =>
  send<void>("POST", "/push/unsubscribe", { endpoint });

export const getPreferences = () => request<Preferences>("/preferences");
export const savePreferences = (data: Preferences) =>
  send<Preferences>("PUT", "/preferences", data);

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
}
