import asyncio
import time


def sync_wait():
    time.sleep(1)


async def async_wait():
    await asyncio.sleep(1)


N = 100


def run_sync():
    start = time.time()
    for _ in range(N):
        sync_wait()
    end = time.time()
    print(f"Sync took {end - start:.2f} seconds")


async def async_main():
    coros = [async_wait() for _ in range(N)]
    await asyncio.gather(*coros)


def run_async():
    start = time.time()
    asyncio.run(async_main())
    end = time.time()
    print(f"Async took {end - start:.2f} seconds")


if __name__ == "__main__":
    # run_sync()
    run_async()
