import asyncio


async def async_fibo(limit):
    a, b = 0, 1
    counter = 0
    while counter < limit:
        counter += 1
        a, b = b, a + b
        yield a
        await asyncio.sleep(1)  # Simulate a delay


async def main():
    async for num in async_fibo(7):
        print(num)


if __name__ == '__main__':
    asyncio.run(main())
