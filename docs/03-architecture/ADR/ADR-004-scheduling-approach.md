# ADR-004: Deterministic greedy scheduler

Status: **Accepted 2026-10-27** (owner delegated to agent recommendation).

## Options
LLM-generated schedule (rejected: unverifiable); constraint solver/CP-SAT (powerful, heavy, hard to explain); **greedy earliest-deadline/slack heuristic with validation** (simple, explainable, testable).

## Decision
Greedy heuristic in a pure module, with property tests and a brute-force comparison on small inputs. The LLM may only phrase explanations from engine-produced facts.

## Consequences
May be sub-optimal in edge cases; always reports unschedulable work honestly. Upgrade path to a solver stays open behind the same function signature.
