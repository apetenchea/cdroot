import asyncio


async def handle_client(reader, writer):
    while True:
        payload = await reader.read(1024)
        if not payload:
            break
        num = payload.decode('utf-8')
        try:
            result = hex(int(num))
        except ValueError:
            result = 'Request payload must be an integer'
        result += '\n'
        writer.write(result.encode('utf-8'))
        await writer.drain()
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 65432)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
