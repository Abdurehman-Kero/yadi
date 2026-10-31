// One command for quality gates:  node scripts/run.mjs check | test | e2e | all
// Runs every step, reports each result, and exits non-zero if any step failed.
import { spawnSync } from "node:child_process";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const api = join(root, "services", "api");
const web = join(root, "apps", "web");
const npm = process.platform === "win32" ? "npm.cmd" : "npm";

const uv = (...args) => ({ cmd: "python", args: ["-m", "uv", "run", ...args], cwd: api });
const npmRun = (script) => ({ cmd: npm, args: ["run", "-s", script], cwd: web, shell: true });

const steps = {
  check: [
    ["API format (ruff)", uv("ruff", "format", "--check", ".")],
    ["API lint (ruff)", uv("ruff", "check", ".")],
    ["API types (mypy strict)", uv("mypy")],
    ["Web format (prettier)", npmRun("format:check")],
    ["Web lint (eslint)", npmRun("lint")],
    ["Web types (tsc)", npmRun("typecheck")],
    ["API contract types up to date", { cmd: process.execPath, args: ["scripts/api-types.mjs", "--check"], cwd: root }],
  ],
  test: [
    ["API tests (pytest)", uv("pytest", "-q")],
    ["Web tests (vitest)", npmRun("test")],
  ],
  e2e: [
    ["Browser tests (playwright + axe)", npmRun("test:e2e")],
  ],
};

const mode = process.argv[2] ?? "all";
const selected = mode === "all" ? [...steps.check, ...steps.test, ...steps.e2e] : steps[mode];
if (!selected) {
  console.error("Usage: node scripts/run.mjs check | test | e2e | all");
  process.exit(2);
}

const results = [];
for (const [name, s] of selected) {
  console.log(`\n=== ${name} ===`);
  const r = spawnSync(s.cmd, s.args, { cwd: s.cwd, stdio: "inherit", shell: s.shell ?? false });
  results.push([name, r.status === 0]);
}
console.log("\n--- Summary ---");
for (const [name, ok] of results) console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
process.exit(results.every(([, ok]) => ok) ? 0 : 1);
