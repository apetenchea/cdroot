import argparse
import httpx
import random
from tqdm import tqdm
from network import Network
from message import Payload


def chaos(ports, req):
    for _ in tqdm(range(req)):
        port = random.choice(ports)
        data = Payload(key=random.randint(0, 100), value=random.randint(0, 1000))
        try:
            httpx.post(f'http://localhost:{port}', json=Network.serialize(data), timeout=30)
        except httpx.HTTPStatusError as e:
            print(f'Error sending message to {port}: {e}')


def check(ports):
    data = dict()
    for port in ports:
        try:
            r = httpx.get(f'http://localhost:{port}')
            r.raise_for_status()
            data[port] = r.json()
        except httpx.HTTPStatusError as e:
            print(f'Error sending message to {port}: {e}')

    for k, v in data.items():
        for k2, v2 in data.items():
            if k == k2:
                continue
            if v != v2:
                print(f'Node {k} is not consistent with node {k2}')
                return

    print('All nodes are consistent')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ports', nargs='+', type=int)
    parser.add_argument('--chaos', type=int, default=0)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.chaos:
        chaos(args.ports, args.chaos)
    if args.check:
        check(args.ports)
