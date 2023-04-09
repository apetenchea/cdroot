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
            return Message(data["sender"], data["timestamp"], data["order"], self.deserialize(data["payload"]))
        else:
            raise ValueError(f"Unknown message type: {data['type']}")

    def process(self, data):
        message = self.deserialize(data)
        if isinstance(message, Message):
            self.process_message(message)
        elif isinstance(message, Payload):
            self.process_payload(message)
        elif isinstance(message, Acknowledgment):
            self.process_ack(message)
        else:
            raise ValueError(f"Unknown message type: {message.__class__.__name__}")

    def process_payload(self, payload):
        message = self.middleware.create_message(payload)
        self.sent.add(message.get_id())
        self.broadcast(message)

    def process_message(self, message):
        if message.get_id() in self.processed:
            # The middleware has already processed this message.
            return

        self.messages[message.get_id()] = message
        self.processed.add(message.get_id())
        self.middleware.append(message)

        # Acknowledge the message.
        ack = self.middleware.create_ack(message)
        self.sent.add(ack.get_id())
        self.broadcast(ack)

        if message.get_id() in self.sent:
            # If the message was created by this node, then it already multicasted it once.
            return

        # Broadcast the message to all nodes.
        self.sent.add(message.get_id())
        self.broadcast(message)

    def process_ack(self, ack):
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
        self.broadcast(ack)

    def broadcast(self, message):
        """
        Broadcast the message to all nodes, unless it has been already forwarded.
        This could be optimized by using a gossip protocol.
        """
        for node in self.nodes:
            try:
                httpx.post(f'{node}', json=self.serialize(message))
            except httpx.HTTPStatusError as e:
                print(f'Error sending message to {node}: {e}')

    def is_acked(self, message):
        return self.ack[message.get_id()] == len(self.nodes)
