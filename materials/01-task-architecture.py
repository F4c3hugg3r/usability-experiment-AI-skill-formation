"""Task 1 — Architecture: Sensor Pipeline.

You are building a small telemetry system. Three independent sensors
(producers) each produce 'data', and a single aggregator consumes and
'processes' it.

Your goal in this task is **not** to implement the processing logic. You can
use functions with empty bodies. Your goal is to set up the architectural
skeleton: the tasks, the nursery, and the way the producers communicate with
the consumer.

## Constraints

- Use `trio` and `trio.open_memory_channel` for communication between
  producers and the consumer.
- The three sensor tasks must run concurrently.
- The consumer must stop cleanly when all producers are done.
"""
