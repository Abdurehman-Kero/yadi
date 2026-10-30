# ADR-002: PostgreSQL and DB-backed reminder queue

Status: **Accepted 2026-10-27** (owner delegated to agent recommendation).

## Problem
Reminders must survive restarts, support delay, retries and idempotency, without unnecessary infrastructure.

## Options
1. In-memory timers — rejected (lost on restart).
2. Redis + BullMQ — robust but adds a service to run, secure, and back up.
3. pg-boss (library over Postgres) — good, but another dependency with its own schema.
4. **Own `reminders` table polled with `FOR UPDATE SKIP LOCKED`** — fits our domain (state machine, attempts table), zero new infrastructure, transactional with task changes.

## Decision
PostgreSQL for all data; option 4 for reminders. Revisit (ADR) if throughput exceeds what polling can serve (not expected at MVP scale; target thousands of reminders/day).

## Consequences
Cancelling a reminder in the same transaction as the task change is trivially consistent. Polling adds ≤5 s latency (acceptable). Worker runs as a separate process from the same codebase.
