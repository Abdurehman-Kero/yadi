// Generates apps/web/src/api/schema.d.ts from the FastAPI OpenAPI document.
// `node scripts/api-types.mjs`          -> regenerate the committed file
// `node scripts/api-types.mjs --check`  -> fail if the committed file is stale
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const api = join(root, "services", "api");
const web = join(root, "apps", "web");
const target = join(web, "src", "api", "schema.d.ts");
const check = process.argv.includes("--check");

const tmp = mkdtempSync(join(tmpdir(), "yadi-openapi-"));
const spec = join(tmp, "openapi.json");
const out = check ? join(tmp, "schema.d.ts") : target;

execFileSync("python", ["-m", "uv", "run", "python", "scripts/export_openapi.py", spec], { cwd: api, stdio: "inherit", env: { ...process.env, PYTHONPATH: "src" } });
const cli = join(web, "node_modules", "openapi-typescript", "bin", "cli.js");
execFileSync(process.execPath, [cli, spec, "-o", out], { cwd: web, stdio: "inherit" });

if (check) {
  const fresh = readFileSync(out, "utf8");
  if (!existsSync(target) || readFileSync(target, "utf8") !== fresh) {
    console.error("API types are stale. Run: node scripts/api-types.mjs");
    process.exit(1);
  }
  console.log("API types are up to date.");
}
