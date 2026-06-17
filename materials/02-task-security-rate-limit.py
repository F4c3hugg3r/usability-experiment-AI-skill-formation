''' Task 2 — Hardening the Aggregator: Resilience

Continue with the pipeline concept. The three sensors represent external IoT devices. They are not fully trusted: any one of them can stall or hang indefinitely.

# Problem
Currently, a stalled sensor slows down the aggregator permanently. We need to ensure the aggregator keeps running, even if it has to wait briefly.

# What to do
Run the starter code below. Sensor 2 (S2) is designed to stall after sending a few values.

Implement a simple Timeout pattern inside the aggregator task with the following requirements:

- Timeout: The aggregator should wait a maximum of 1.0 second for the next value from the channel.
- Warning: If the waiting period times out, log a general warning print statement and continue to the next loop iteration.

# Constraints
Use trio's built-in mechanisms for time-based behavior.

Do not modify the sensor code.
'''
import trio

async def main():
    send, receive = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(sensor, send.clone(), "S1", 0.5)
        nursery.start_soon(sensor, send.clone(), "S3", 0.5)
        # S2 will stall after 3 iterations
        nursery.start_soon(sensor, send.clone(), "S2", 0.5, 3)
        
        nursery.start_soon(aggregator, receive.clone())

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
    """Naive aggregator: no timeout, no warning."""
    async for sensor_id, value in receive_channel:
        print(f"[Aggregator] Processed value from {sensor_id}: {value}")

if __name__ == "__main__":
    trio.run(main)

