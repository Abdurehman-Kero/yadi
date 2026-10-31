import type { Metadata } from "next";
import { TasksScreen } from "@/features/tasks/TasksScreen";

export const metadata: Metadata = { title: "Tasks · Yadi" };

export default function TasksPage() {
  return (
    <>
      <h1>Tasks</h1>
      <TasksScreen />
    </>
  );
}
