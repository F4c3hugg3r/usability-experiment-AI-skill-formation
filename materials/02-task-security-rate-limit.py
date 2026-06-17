"""Task 2 — Hardening the Aggregator: A Stalled Sensor.

Continue with the pipeline from Task 1. The three sensors represent
external IoT devices. They are not fully trusted: any one of them can stop
responding at any time — a dropped network connection, a firmware hang, a
blocked synchronous call.

## Problem

A stalled sensor should not be able to block or slow down the whole
pipeline. If one sensor goes silent, the aggregator should still make
progress on the data coming from the other two, and the operator should
be told that something is wrong.

## What to do

1. Run the starter below. The aggregator keeps printing values from the well-behaved sensors, 
but it has no way to tell that the stalled sensor has gone silent — its silence is invisible 
to the consumer. The operator never finds out that one of the three sensors is dead.

2. Implement the protection inside the aggregator: a per-sensor timeout, a warning log naming 
the affected sensor when the timeout fires, and continued processing of the well-behaved sensors.

## Constraints

- Use `trio`'s built-in mechanisms for time-based behavior.
- The protection must be enforced inside the aggregator, not by trusting
  the producers.
- The well-behaved sensors must keep working while one is stalled.
- On timeout, the aggregator logs a warning naming the affected sensor.
"""

import trio


async def sensor(send_channel, sensor_id, tick, stall_after=None):
    """Send values forever; if `stall_after` is set, stop sending after that many."""
    i = 0
    async with send_channel:
        while True:
            await send_channel.send(f"{sensor_id}:{i}")
            if stall_after is not None and i >= stall_after:
                await trio.sleep_forever()
            await trio.sleep(tick)
            i += 1


async def aggregator(receive_channel):
    """Naive aggregator: no per-sensor timeout, blocks when the channel goes quiet."""
    async for item in receive_channel:
        print(f"aggregator got: {item}")


async def main():
    send, receive = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(sensor, send.clone(), "S1", 0.5)
        nursery.start_soon(sensor, send.clone(), "S2", 0.5, 2)
        nursery.start_soon(sensor, send.clone(), "S3", 0.5)
        nursery.start_soon(aggregator, receive.clone())


if __name__ == "__main__":
    trio.run(main)
