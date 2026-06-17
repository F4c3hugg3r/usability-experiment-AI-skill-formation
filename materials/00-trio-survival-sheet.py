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

async def demo_nursery():
    """Run two workers in a nursery; the context waits for both to finish."""
    async with trio.open_nursery() as nursery:
        nursery.start_soon(_worker, "A")
        nursery.start_soon(_worker, "B")

async def _worker(name):
    """Toy task: prints before/after a cooperative sleep."""
    print(f"{name} starting")
    await trio.sleep(1)
    print(f"{name} done")


# ## 2. Memory Channels (Send / Receive)
#
# Channels are how tasks communicate. `trio.open_memory_channel(max_buffer)`
# returns a `(send_channel, receive_channel)` pair.
# `send_channel.clone()` creates a new send handle. 
#
# You can read from a channel using `async for` (which handles closure automatically)
# OR manually using `await receive_channel.receive()`, which requires handling
# the `trio.EndOfChannel` exception when all senders are gone.

async def demo_channels():
    """Wire one producer to one consumer via a rendezvous channel."""
    send, receive = trio.open_memory_channel(0)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(_channel_producer, send)
        nursery.start_soon(_channel_consumer, receive)

async def _channel_producer(send_channel: trio.MemorySendChannel):
    """Send three values then close the channel."""
    async with send_channel:
        for i in range(3):
            await send_channel.send(i)

async def _channel_consumer(receive_channel):
    """Manually drain the channel to allow for explicit control (like timeouts)."""
    async with receive_channel:
        while True:
            try:
                item = await receive_channel.receive()
                print(f"got: {item}")
            except trio.EndOfChannel:
                print("Channel closed, stopping consumer.")
                break


# ## 3. Timeouts and Cancellation
#
# `trio.move_on_after(delay)` cancels the current scope after a delay.
# `trio.fail_after(delay)` raises an exception instead. Inside a cancelled
# block, you can check `cancel_scope.cancelled_caught` to see if it timed out.

async def demo_timeout():
    """Cancel a slow operation after 2s and continue without raising."""
    
    with trio.move_on_after(2) as cancel_scope:
        await _slow_op()
    
    if cancel_scope.cancelled_caught:
        print("Operation timed out, moving on")

async def _slow_op():
    """Stand-in for a long-running awaitable used to demo cancellation."""
    await trio.sleep(10)
    

# ## 4. Blocking the Event Loop
#
# Trio is single-threaded with cooperative multitasking: the loop only
# switches tasks at `await` points. A synchronous blocking call (e.g.
# `time.sleep`) freezes the whole program.
# Use `trio.to_thread.run_sync(...)` to run blocking work off the loop.

async def _run_all_demos():
    """Entry point: run every demo in sequence."""
    await demo_nursery()
    await demo_channels()
    await demo_timeout()


if __name__ == "__main__":
    trio.run(_run_all_demos)