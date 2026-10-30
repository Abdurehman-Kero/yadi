# Scheduling Engine

A pure, deterministic Python module (`yadi/modules/scheduling`): `generate_schedule(input) → { blocks, unscheduled[], conflicts[], explanations[] }`. No I/O, no clock reads (`now` is an input), no LLM.

## Inputs
Tasks (status, priority, due, duration, dependencies, fixed/flexible, preferred period), fixed events, user preferences (zone, working hours, buffer, unavailable ranges), window (from–to), `now`.

## Hard constraints (never violated)
1. Blocks lie within working hours and outside unavailable ranges.
2. Fixed events are never moved or overlapped.
3. No two blocks overlap; buffer between blocks is respected.
4. A task starts after its dependencies end.
5. Total scheduled minutes for a task ≤ its estimate (split allowed; min chunk configurable, default 25 min).
6. All math in the user's timezone, DST-aware (a local day may have 23/25 hours).

## Soft preferences (ordered)
Meet deadline → priority → preferred period → earlier start for nearer deadlines → fewer splits.

## Algorithm (MVP)
1. Place fixed events as immovable blocks.
2. Compute free intervals in window.
3. Order flexible tasks by: topological order of dependencies, then slack = (deadline − now − remaining duration) ascending, then priority, then created_at (stable tie-break → deterministic).
4. Greedy place each task into earliest suitable free interval(s) before its deadline, honoring preferred period when possible.
5. Anything that cannot meet its deadline goes to `unscheduled` with a reason (`NO_CAPACITY_BEFORE_DEADLINE`, `DEPENDENCY_UNSCHEDULED`, `OUTSIDE_WINDOW`, …) and alternatives (extend deadline, drop lower-priority task X, free N minutes).
Greedy is chosen for explainability; optimization is a possible later ADR. Because it is greedy it can miss feasible plans; the test suite includes a brute-force checker on small cases to measure this.

## Priority vs position
Priority influences ordering only among tasks competing for time; it does not override fixed events or dependencies.

## Locked blocks
User-edited blocks are `locked`; regeneration treats them as fixed.

## Testing
Property tests: no overlaps, inside windows, fixed events intact, dependencies ordered, determinism (same input → same output), DST-day cases, over-capacity cases.
