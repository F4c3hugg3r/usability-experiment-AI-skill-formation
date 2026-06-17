"""Task 3 — Debugging: Cascading Failures in the Pipeline

The program below simulates a telemetry system reading data chunks from two sensors and running a simulated database heartbeat. All operations are supposed to run concurrently in a `trio.nursery`.

## Symptom

When you run the file, everything starts fine. However, after a short time, Sensor-2 receives corrupt data and crashes. The critical issue is that **Sensor-1 and the Database heartbeat also instantly crash**, taking down the entire system. 

## What to do

1. Run the file and observe the crash. Examine the traceback in your terminal. Note how the failure of one isolated sensor task propagates.
2. Fix the pipeline so that a failure in one sensor task does **not** bring down the `nursery` and the other running tasks. 
3. If a sensor fails, it should log its specific error, but the rest of the system (Sensor-1 and the DB) must keep running and finish their execution gracefully.

## Constraints

- Do not remove the `raise ValueError` from the `fetch_sensor_data` function — simulating unpredictable external errors is the point.
- The solution must isolate the failure without changing the overarching `nursery` structure in `main()`.
"""

import trio

async def fetch_sensor_data(sensor_id, fail_on_iteration=None):
    """Fetches data, but crashes if corrupt data is encountered."""
    for i in range(5):
        print(f"[{sensor_id}] Fetching data chunk {i}...")
        await trio.sleep(0.5)
        
        # Simulate an unexpected error (corrupt data parsing, etc.)
        if fail_on_iteration == i:
            raise ValueError(f"Corrupt data received from {sensor_id} at chunk {i}!")
            
        print(f"[{sensor_id}] Data chunk {i} processed successfully.")

async def database_heartbeat():
    """Simulates an independent, ongoing background task."""
    for i in range(5):
        print("[DB] Heartbeat: Database connection active...")
        await trio.sleep(0.6)
    print("[DB] Connection closed safely.")

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(fetch_sensor_data, "Sensor-1", None)
        # Sensor-2 will encounter corrupt data on iteration 2
        nursery.start_soon(fetch_sensor_data, "Sensor-2", 2) 
        nursery.start_soon(database_heartbeat)

if __name__ == "__main__":
    trio.run(main)
