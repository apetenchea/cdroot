import argparse
import asyncio
import httpx
import random
from tqdm import tqdm
from network import Network
from message import Payload


async def chaos(ports, rounds, parallel):
    for _ in tqdm(range(rounds)):
        data = [(random.choice(ports), Payload(key=random.randint(0, 100), value=random.randint(0, 1000)))
                for _ in range(parallel)]
        async with httpx.AsyncClient() as client:
            await asyncio.gather(*[client.post(f'http://localhost:{port}', json=Network.serialize(d))
                                   for port, d in data])


async def check(ports):
    data = dict()
    async with httpx.AsyncClient() as client:
        for port in ports:
            r = await client.get(f'http://localhost:{port}')
            r.raise_for_status()
            data[port] = r.json()

    for k, v in data.items():
        for k2, v2 in data.items():
            if k == k2:
                continue
            if v != v2:
                print(f'Node {k} is not consistent with node {k2}')
                return

    print('All replicas are consistent')


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ports', nargs='+', type=int)
    parser.add_argument('--chaos', type=int, default=0)
    parser.add_argument('--parallel', type=int, default=1)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.chaos:
        await chaos(args.ports, args.chaos, args.parallel)
    if args.check:
        await check(args.ports)

if __name__ == '__main__':
    asyncio.run(main())
