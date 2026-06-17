'''Task 2 — Hardening the Aggregator: Resilience & Circuit Breaker

Continue with the pipeline concept. The three sensors represent external IoT devices. They are not fully trusted: any one of them can stall or hang indefinitely. 

## Problem

Currently, a stalled sensor slows down the aggregator. Even worse, if a sensor fails repeatedly, the system wastes resources waiting for it instead of isolating the problem. 

## What to do

1. Run the starter code below. Sensor 2 (`S2`) is designed to stall after sending a few values. Notice how the aggregator just waits and stops logging progress for `S2` without taking further action.
2. Implement a **Circuit Breaker** pattern inside the `aggregator` task with the following requirements:
   - **Timeout:** The aggregator should wait a maximum of `1.0` second for a value from any sensor.
   - **State Tracking:** If a sensor times out, log a warning. Keep track of how many times *each* sensor has timed out consecutively.
   - **Quarantine (Circuit Breaker):** If a specific sensor times out 3 times in a row, mark it as "quarantined". Once quarantined, the aggregator must stop waiting for this sensor entirely and ignore it for the rest of the program's lifecycle.
   - **Continued Progress:** Well-behaved sensors must continue to be processed without delay.

## Constraints

- Use `trio`'s built-in mechanisms for time-based behavior.
- The protection and state tracking must be enforced strictly inside the `aggregator` function. Do not modify the `sensor` code.
'''
import trio

async def sensor(send_channel, sensor_id, tick, stall_after=None):
    """Send values; if `stall_after` is set, stop sending after that many."""
    i = 0
    async with send_channel:
        while True:
            await send_channel.send((sensor_id, i))
            if stall_after is not None and i >= stall_after:
                # Simulate a permanent hang in the sensor
                await trio.sleep_forever()
            await trio.sleep(tick)
            i += 1

async def aggregator(receive_channel):
    """Naive aggregator: no timeout, no failure tracking."""
    async for sensor_id, value in receive_channel:
        print(f"[Aggregator] Processed value from {sensor_id}: {value}")

async def main():
    send, receive = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(sensor, send.clone(), "S1", 0.5)
        # S2 will stall after 3 iterations
        nursery.start_soon(sensor, send.clone(), "S2", 0.5, 3)
        nursery.start_soon(sensor, send.clone(), "S3", 0.5)
        
        nursery.start_soon(aggregator, receive.clone())

if __name__ == "__main__":
    trio.run(main)