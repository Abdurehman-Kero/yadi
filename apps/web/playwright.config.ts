import { defineConfig, devices } from "@playwright/test";

const API_PORT = 8100;
const WEB_PORT = 3100;
const env = {
  ENVIRONMENT: "development",
  DEV_IDENTITY_ENABLED: "true",
  DATABASE_URL: "postgresql+psycopg://yadi:yadi_dev_password@127.0.0.1:5433/yadi_e2e",
  PYTHONPATH: "src",
  // Browser tests must never reach real services, whatever is in .env.
  GEMINI_API_KEY: "",
  VAPID_PUBLIC_KEY: "",
  VAPID_PRIVATE_KEY: "",
};

// Uses its own database, ports and build folder, so dev data and dev servers are untouched.
export default defineConfig({
  testDir: "./e2e",
  workers: 1, // The tests share one database and one dev user.
  fullyParallel: false,
  timeout: 60_000,
  reporter: "list",
  use: { baseURL: `http://127.0.0.1:${WEB_PORT}`, ...devices["Desktop Chrome"] },
  webServer: [
    {
      command: `python -m uv run python scripts/prepare_e2e_db.py && python -m uv run uvicorn --app-dir src --factory yadi.main:create_app --port ${API_PORT}`,
      cwd: "../../services/api",
      url: `http://127.0.0.1:${API_PORT}/api/v1/health/ready`,
      env,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      // A real worker: browser tests see reminders exactly as a user would.
      command: "python -m uv run python -m yadi.worker",
      cwd: "../../services/api",
      env: { ...env, WORKER_POLL_SECONDS: "1" },
      reuseExistingServer: false,
    },
    {
      command: `npx next dev -p ${WEB_PORT}`,
      url: `http://127.0.0.1:${WEB_PORT}`,
      env: { API_INTERNAL_URL: `http://127.0.0.1:${API_PORT}`, NEXT_DIST_DIR: ".next-e2e" },
      reuseExistingServer: false,
      timeout: 180_000,
    },
  ],
});
