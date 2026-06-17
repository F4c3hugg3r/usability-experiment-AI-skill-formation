"""Trio Survival Sheet.

A quick reference for working with async Python using the `trio` library.
Use this while you work through the tasks — you do not need to memorize it.
"""

import trio


# ## 1. Nurseries
#
# A nursery is a context manager that groups concurrent tasks. When the
# context exits, it waits for all started tasks to finish. If any task crashes 
# (i.e., an exception is raised and not caught inside the task), the whole 
# nursery cancels all other tasks.


async def _worker(name):
    """Toy task: prints before/after a cooperative sleep."""
    print(f"{name} starting")
    # await yields control to the event loop; other tasks can run during this sleep
    await trio.sleep(1)
    print(f"{name} done")


async def demo_nursery():
    """Run two workers in a nursery; the context waits for both to finish."""
    # nursery: groups concurrent tasks, waits for all on exit, cancels siblings on error
    async with trio.open_nursery() as nursery:
        nursery.start_soon(_worker, "A")
        nursery.start_soon(_worker, "B")


# ## 2. Memory Channels (Send / Receive)
#
# Channels are how tasks communicate. `trio.open_memory_channel(max_buffer)`
# returns a `(send_channel, receive_channel)` pair. A channel is *bounded*:
# `send` blocks once the buffer is full, `receive` blocks if no item is
# available.
#
# `send_channel.clone()` creates a new send handle. Use
# `async with send_channel:` to make sure the receiver stops when the last
# sender is done.


async def _channel_producer(send_channel):
    """Send three values, pause, then send a sentinel to stop the consumer."""
    # `async with` closes the channel on exit, ending the consumer's loop
    async with send_channel:
        for i in range(3):
            # send blocks while the buffer is full (or until a receiver is ready)
            await send_channel.send(i)
        await trio.sleep(3)
        await send_channel.send("stop")


async def _channel_consumer(receive_channel):
    """Drain the channel until the sentinel arrives, then return."""
    async with receive_channel:
        # iterates until the channel is closed and drained
        async for item in receive_channel:
            print(f"got: {item}")
            if item == "stop":
                return


async def demo_channels():
    """Wire one producer to one consumer via a rendezvous channel (buffer=0)."""
    # max_buffer=0: send and receive must rendezvous (no buffering)
    send, receive = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        # each sender/receiver needs its own handle via .clone()
        nursery.start_soon(_channel_producer, send.clone())
        nursery.start_soon(_channel_consumer, receive.clone())


# ## 3. Timeouts and Cancellation
#
# `trio.move_on_after(delay)` cancels the current scope after a delay.
# `trio.fail_after(delay)` raises an exception instead. Inside a cancelled
# block, you can check `trio.current_cancelled_caught()`.


async def _slow_op():
    """Stand-in for a long-running awaitable used to demo cancellation."""
    await trio.sleep(10)


async def demo_timeout():
    """Cancel a slow operation after 2s and continue without raising."""
    # cancel this scope after 2s; no exception raised, execution continues after `with`
    with trio.move_on_after(2):
        await _slow_op()
    print("timed out, moving on")


# ## 4. Blocking the Event Loop
#
# Trio is single-threaded with cooperative multitasking: the loop only
# switches tasks at `await` points. A synchronous blocking call (e.g.
# `time.sleep`, blocking I/O, or a CPU-heavy loop) freezes the whole program.
# Use `trio.to_thread.run_sync(...)` to run blocking work off the loop.


# ## 5. Sleeping
#
# In async code use `await trio.sleep(seconds)` — never `time.sleep`.


async def _run_all_demos():
    """Entry point: run every demo in sequence under a single trio event loop."""
    await demo_nursery()
    await demo_channels()
    await demo_timeout()


if __name__ == "__main__":
    trio.run(_run_all_demos)
