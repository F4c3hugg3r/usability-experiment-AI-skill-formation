# Usability Experiment: Secure Telemetry Pipeline

A short study material suite designed to evaluate how a Socratic AI
coding assistant handles different skill triggers (architect, security-rated
code, debugging) when students work on a realistic async Python task.

## Structure

- `materials/00-trio-survival-sheet.py` — concise reference for the relevant
  `trio` concepts (nurseries, channels, timeouts, event loop). Students use
  this as a lookup while talking to the AI.
- `materials/01-task-architecture.py` — Task 1: design a producer/consumer
  sensor pipeline architecture.
- `materials/02-task-security-rate-limit.py` — Task 2: harden the aggregator
  against a stalled (non-responsive) sensor. The starter script
  intentionally stalls one of three sensors so the symptom is observable.
- `materials/03-task-debugging-eventloop.py` — Task 3: debug a frozen
  pipeline caused by a synchronous sleep in async code. Run this file to
  reproduce the symptom (the sensors stay silent until the blocking
  database call returns).

# TODO adjust task 2 and 3 