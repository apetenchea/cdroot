import asyncio
import httpx
from message import Payload, Acknowledgment, Message


class Network:
    """
    Network layer. Keeps track of sent messages and their acknowledgments.
    Connects to the middleware layer.
    """
    def __init__(self, nodes, middleware):
        self.nodes = nodes
        self.middleware = middleware
        self.messages = dict()
        self.sent = set()  # Sent messages
        self.processed = set()  # Messages already processed by the middleware
        self.ack = dict()  # Mapping between message IDs and the number of acknowledgments received
        self.acked = set()  # Messages that have been acknowledged

    @classmethod
    def serialize(cls, data):
        d = data.to_dict()
        d['type'] = data.__class__.__name__.lower()
        return d

    def deserialize(self, data):
        if data["type"] == "payload":
            return Payload(data["key"], data["value"])
        elif data["type"] == "acknowledgment":
            return Acknowledgment(data["msg_timestamp"], data["msg_sender"],
                                  data["ack_timestamp"], data["ack_sender"])
        elif data["type"] == "message":
            return Message(data["sender"], data["timestamp"], data["order"], Payload(**data["payload"]))
        else:
            raise ValueError(f"Unknown message type: {data['type']}")

    async def process(self, data):
        message = self.deserialize(data)
        if isinstance(message, Message):
            await self.process_message(message)
        elif isinstance(message, Payload):
            await self.process_payload(message)
        elif isinstance(message, Acknowledgment):
            await self.process_ack(message)
        else:
            raise ValueError(f"Unknown message type: {message.__class__.__name__}")

    async def process_payload(self, payload):
        message = self.middleware.create_message(payload)
        self.sent.add(message.get_id())
        await self.broadcast(message)

    async def process_message(self, message):
        if message.get_id() in self.processed:
            # The middleware has already processed this message.
            return

        self.messages[message.get_id()] = message
        self.processed.add(message.get_id())
        self.middleware.append(message)

        # Acknowledge the message.
        ack = self.middleware.create_ack(message)
        self.sent.add(ack.get_id())
        await self.broadcast(ack)

        if message.get_id() in self.sent:
            # If the message was created by this node, then it already multicasted it once.
            return

        # Broadcast the message to all nodes.
        self.sent.add(message.get_id())
        await self.broadcast(message)

    async def process_ack(self, ack):
        if ack.get_id() in self.processed:
            # The middleware has already processed this acknowledgment.
            return

        # Acknowledge the message locally.
        self.processed.add(ack.get_id())
        acked_id = ack.get_acked_id()
        self.ack.setdefault(acked_id, 0)
        self.ack[acked_id] += 1
        if self.is_acked(acked_id):
            self.acked.add(acked_id)
            self.middleware.consume(self.acked)

        if ack.get_id() in self.sent:
            # If the acknowledgement was already broadcast, don't do it again.
            return
        self.sent.add(ack.get_id())
        await self.broadcast(ack)

    async def broadcast(self, message):
        """
        Broadcast a message to all nodes.
        This could be optimized using a gossip protocol.
        """
        tasks = []
        async with httpx.AsyncClient() as client:
            for node in self.nodes:
                task = asyncio.create_task(client.post(f'{node}', json=self.serialize(message), timeout=30))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for url, result in zip(self.nodes, results):
                if isinstance(result, Exception):
                    print(f'{url}: {result}')

    def is_acked(self, message_id):
        return self.ack[message_id] == len(self.nodes)
