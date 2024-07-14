import asyncio


class AsyncFibo:
    def __init__(self, limit):
        self.a, self.b = 0, 1
        self.counter = 0
        self.limit = limit

    def __aiter__(self):
        return self

    async def __anext__(self):
        self.counter += 1
        if self.counter > self.limit:
            raise StopAsyncIteration
        self.a, self.b = self.b, self.a + self.b
        await asyncio.sleep(1)  # Simulate a delay
        return self.a


async def main():
    async for num in AsyncFibo(7):
        print(num)


if __name__ == '__main__':
    asyncio.run(main())
