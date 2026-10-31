import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const unique = () => `Task ${Date.now()}-${Math.floor(Math.random() * 1000)}`;

async function openForm(page: Page) {
  await page.getByRole("button", { name: "New task" }).click();
}

async function addTask(page: Page, title: string) {
  await openForm(page);
  await page.getByLabel("Title", { exact: true }).fill(title);
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("status").filter({ hasText: `Added "${title}"` })).toBeVisible();
}

const row = (page: Page, title: string) =>
  page.getByRole("listitem").filter({ has: page.getByRole("heading", { name: title }) });

test.beforeEach(async ({ page }) => {
  await page.goto("/tasks");
  await expect(page.getByRole("button", { name: "New task" })).toBeVisible();
});

test("a task survives a refresh and moves through its whole life", async ({ page }) => {
  const title = unique();
  await addTask(page, title);
  await expect(row(page, title).getByText("Inbox")).toBeVisible();

  await page.reload();
  await expect(row(page, title)).toBeVisible();

  await row(page, title).getByRole("button", { name: /^Edit/ }).click();
  await page
    .getByLabel(/Estimate/)
    .last()
    .fill("45");
  await page.getByLabel("Due (optional)").last().fill("2035-06-01T09:30");
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(row(page, title).getByText("45 min")).toBeVisible();
  await expect(row(page, title).getByText("Planned")).toBeVisible();

  await row(page, title)
    .getByRole("button", { name: /^Start/ })
    .click();
  await expect(row(page, title).getByText("In progress")).toBeVisible();

  await row(page, title)
    .getByRole("button", { name: /^Complete/ })
    .click();
  await expect(row(page, title)).toHaveCount(0);
  await page.getByRole("button", { name: "Completed", exact: true }).click();
  await expect(row(page, title)).toBeVisible();

  await row(page, title)
    .getByRole("button", { name: /^History/ })
    .click();
  for (const label of ["Created", "Edited", "Started"]) {
    await expect(row(page, title).getByRole("listitem").filter({ hasText: label })).toBeVisible();
  }

  await row(page, title)
    .getByRole("button", { name: /^Reopen/ })
    .click();
  await page.getByRole("button", { name: "Active", exact: true }).click();
  await expect(row(page, title).getByText("Planned")).toBeVisible();
});

test("cancelling asks first, and the task stays on record", async ({ page }) => {
  const title = unique();
  await addTask(page, title);
  await row(page, title)
    .getByRole("button", { name: /^Cancel task/ })
    .click();
  await row(page, title).getByRole("button", { name: "Keep task" }).click();
  await expect(row(page, title).getByText("Inbox")).toBeVisible();

  await row(page, title)
    .getByRole("button", { name: /^Cancel task/ })
    .click();
  await row(page, title).getByRole("button", { name: "Yes, cancel task" }).click();
  await expect(row(page, title)).toHaveCount(0);
  await page.getByRole("button", { name: "Cancelled", exact: true }).click();
  await expect(row(page, title)).toBeVisible();
});

test("a server failure shows a message and keeps what was typed", async ({ page }) => {
  await page.route("**/api/v1/tasks", (route) =>
    route.request().method() === "POST" ? route.abort() : route.continue(),
  );
  await openForm(page);
  await page.getByLabel("Title", { exact: true }).fill("Do not lose me");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Could not reach Yadi" })).toBeVisible();
  await expect(page.getByLabel("Title", { exact: true })).toHaveValue("Do not lose me");
});

test("changing the timezone changes the time shown, not the moment", async ({ page }) => {
  const title = unique();
  await openForm(page);
  await page.getByLabel("Title", { exact: true }).fill(title);
  await page.getByLabel("Due (optional)").fill("2035-01-15T10:00");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(row(page, title).getByText(/10:00/)).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Settings" }).click();
  const zone = page.getByLabel("Timezone");
  const original = await zone.inputValue();
  await zone.selectOption(original === "Asia/Tokyo" ? "UTC" : "Asia/Tokyo");
  await page.getByRole("button", { name: "Save settings" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Settings saved." })).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Tasks" }).click();
  await expect(row(page, title).getByText(/Due .*\d\d:00/)).toBeVisible();
  await expect(row(page, title).getByText(/10:00/)).toHaveCount(0);

  await page.goto("/settings");
  await page.getByLabel("Timezone").selectOption(original);
  await page.getByRole("button", { name: "Save settings" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Settings saved." })).toBeVisible();
});

test("a task can be added with the keyboard alone", async ({ page }) => {
  const title = unique();
  await openForm(page);
  await page.getByLabel("Title", { exact: true }).focus();
  await page.keyboard.type(title);
  await page.keyboard.press("Enter");
  await expect(row(page, title)).toBeVisible();
});

test("without an AI key, Tell Yadi falls back to the manual form", async ({ page }) => {
  await page.goto("/");
  const title = unique();
  await page.getByLabel("Your message").fill(title);
  await page.getByRole("button", { name: "Understand" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "not available" })).toBeVisible();
  await page.getByRole("button", { name: "Save task" }).click();
  await expect(page.getByRole("status").filter({ hasText: `Added "${title}"` })).toBeVisible();
  await page.goto("/tasks");
  await expect(row(page, title)).toBeVisible();
});

test("a draft is reviewed and corrected before it is saved", async ({ page }) => {
  await page.goto("/");
  const title = unique();
  await page.route("**/api/v1/assistant/extract", (route) =>
    route.fulfill({
      json: {
        note: null,
        drafts: [
          {
            title: "Wrong title",
            description: null,
            dueAt: "2035-03-01T09:00:00Z",
            duePhrase: "March 1st",
            estimatedMinutes: 120,
            priority: "high",
            confidence: "high",
            questions: [{ field: "due", question: "What time on March 1st?" }],
          },
        ],
      },
    }),
  );
  await page.getByLabel("Your message").fill("finish my report by March 1st");
  await page.getByRole("button", { name: "Understand" }).click();
  await expect(page.getByText("What time on March 1st?")).toBeVisible();

  const results = new AxeBuilder({ page }).include("#main");
  const serious = (await results.analyze()).violations.filter((v) =>
    ["serious", "critical"].includes(v.impact!),
  );
  expect(serious.map((v) => v.id)).toEqual([]);

  const draftTitle = page.getByLabel("Title", { exact: true }).first();
  await draftTitle.fill(title);
  await page.getByRole("button", { name: "Save task" }).click();
  await expect(page.getByRole("status").filter({ hasText: `Added "${title}"` })).toBeVisible();
  await page.goto("/tasks");
  await expect(row(page, title).getByText("120 min")).toBeVisible();
  await expect(row(page, title).getByText("Planned")).toBeVisible();
});

test("Yadi plans around a fixed event, explains it, and reports what does not fit", async ({
  page,
}) => {
  const fixedTitle = `Meeting ${unique()}`;
  const flexibleTitle = `Report ${unique()}`;
  const hugeTitle = `Huge ${unique()}`;
  const day = new Date(Date.now() + 2 * 86_400_000).toISOString().slice(0, 10);

  await openForm(page);
  await page.getByLabel("Title", { exact: true }).fill(fixedTitle);
  await page.getByLabel(/fixed time/).check();
  await page.getByLabel("Starts").fill(`${day}T09:00`);
  await page.getByLabel("Ends").fill(`${day}T10:00`);
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(row(page, fixedTitle).getByText("Fixed", { exact: true })).toBeVisible();

  await page.getByLabel("Title", { exact: true }).fill(flexibleTitle);
  await page.getByLabel(/Estimate/).fill("60");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(row(page, flexibleTitle)).toBeVisible();

  await page.getByLabel("Title", { exact: true }).fill(hugeTitle);
  await page.getByLabel(/Estimate/).fill("1440");
  await page.getByLabel("Due (optional)").fill(`${day}T10:00`);
  await page.getByLabel("Priority").selectOption("critical");
  await page.getByRole("button", { name: "Add task" }).click();
  await expect(row(page, hugeTitle)).toBeVisible();

  await page.getByRole("navigation").getByRole("link", { name: "Schedule" }).click();
  await page.getByRole("button", { name: /Plan my week|Replan/ }).click();
  await expect(page.getByRole("status").filter({ hasText: "Plan updated" })).toBeVisible();

  const fixedBlock = row(page, fixedTitle);
  await expect(fixedBlock.getByText("Fixed", { exact: true })).toBeVisible();
  await expect(fixedBlock.getByRole("button", { name: /^Move/ })).toHaveCount(0);
  const planned = row(page, flexibleTitle);
  await expect(planned.getByText("Flexible")).toBeVisible();
  await expect(planned.getByText(/No deadline/)).toBeVisible();
  const missing = page.getByRole("listitem").filter({ hasText: hugeTitle });
  await expect(missing.getByText(/do not fit before the deadline/)).toBeVisible();
  await expect(missing.getByText(/Move the deadline later/)).toBeVisible();

  await page.goto("/");
  await expect(page.getByText("Next up")).toBeVisible();
  await page.goto("/schedule");
  await planned.getByRole("button", { name: /^Move/ }).click();
  await planned.getByLabel("New start").fill(`${day}T03:00`);
  await planned.getByLabel("New end").fill(`${day}T04:00`);
  await planned.getByRole("button", { name: "Save time" }).click();
  await expect(planned.getByRole("alert")).toContainText("outside your working hours");

  await planned.getByLabel("New start").fill(`${day}T15:00`);
  await planned.getByLabel("New end").fill(`${day}T16:00`);
  await planned.getByRole("button", { name: "Save time" }).click();
  await expect(planned.getByText("Kept in place")).toBeVisible();

  await page.getByRole("button", { name: "Replan" }).click();
  await expect(page.getByRole("status").filter({ hasText: "Plan updated" })).toBeVisible();
  await expect(planned.getByText("Kept in place")).toBeVisible();
});

for (const colorScheme of ["light", "dark"] as const) {
  for (const path of ["/", "/schedule", "/tasks", "/settings"]) {
    test(`no serious accessibility problems on ${path} in ${colorScheme} mode`, async ({
      page,
    }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(path);
      await page.waitForLoadState("networkidle");
      await expect(page.getByRole("status").filter({ hasText: "Loading" })).toHaveCount(0);
      const results = await new AxeBuilder({ page }).analyze();
      const serious = results.violations.filter((v) => ["serious", "critical"].includes(v.impact!));
      expect(serious.map((v) => `${v.id}: ${v.help}`)).toEqual([]);
    });
  }
}
