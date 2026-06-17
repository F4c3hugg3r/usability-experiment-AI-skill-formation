"""Task 3 — Debugging: A Pipeline That Freezes.

The program below is supposed to read from two sensors and write a summary
to a database — all three operations in parallel.

## Symptom

When you run the file, the program takes about 5 seconds to finish — but
not because the sensors are slow; the database save is. The two sensor
tasks do not print *anything* until the database save has fully completed.
The pipeline is effectively serial: the `time.sleep(5)` inside
`save_to_database` blocks the single trio event-loop thread, so the
sensors cannot make progress at all until it returns.

## What to do

1. Run the file and observe the symptom yourself. Note the order of the print 
lines and how long the program takes.

2. Fix the pipeline so that all three operations actually run concurrently 
(you should see the sensor prints before the database save finishes).

## Constraints

- The three tasks must genuinely run in parallel after the fix.
- Do not just delete the slow database operation — simulate the work that
  would happen in a real program (e.g. a real DB driver that blocks).
"""

import time

import trio


async def fetch_sensor_data(sensor_id):
    print(f"[{sensor_id}] Fetching data...")
    await trio.sleep(1)
    print(f"[{sensor_id}] Data received.")


async def save_to_database():
    print("[DB] Saving data to database...")
    time.sleep(5)
    print("[DB] Data saved successfully.")


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(fetch_sensor_data, "Sensor-1")
        nursery.start_soon(fetch_sensor_data, "Sensor-2")
        nursery.start_soon(save_to_database)


trio.run(main)
