import heapq
from message import Message, Acknowledgment


class Middleware:
    def __init__(self, name, application):
        self.name = name  # Node ID
        self.application = application  # Application layer
        self.clock = 0  # Lamport clock
        self.sent = 0  # Number of messages sent by this node
        self.queue = []  # Queue of messages to be delivered
        self.delivered = dict()  # Mapping between nodes and the number of messages delivered from them

    def create_message(self, payload):
        # A node will also send the message and acknowledgment to itself.
        self.clock += 1
        self.sent += 1
        message = Message(self.name, self.clock, self.sent, payload)
        return message

    def create_ack(self, message):
        self.clock += 1
        # We don't need to increment the sent counter, because acknowledgements don't count towards the total order.
        return Acknowledgment(message.timestamp, message.sender, self.clock, self.name)

    def append(self, message):
        self.clock = max(self.clock, message.timestamp) + 1
        heapq.heappush(self.queue, message)

    def consume(self, acked):
        while self.queue:
            top = self.queue[0]
            if top.get_id() not in acked:
                # The top message is not yet acknowledged by all nodes.
                break
            if top.order == self.delivered.get(top.sender, 0) + 1:
                # The top message is the next message to be delivered from its sender.
                heapq.heappop(self.queue)
                self.delivered[top.sender] = top.order
                self.application.process(top.get_id(), top.payload)
