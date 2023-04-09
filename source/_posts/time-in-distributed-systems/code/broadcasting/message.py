class Acknowledgment:
    def __init__(self, msg_timestamp, msg_sender, ack_timestamp, ack_sender):
        self.msg_timestamp = msg_timestamp
        self.msg_sender = msg_sender
        self.ack_timestamp = ack_timestamp
        self.ack_sender = ack_sender

    def to_dict(self):
        return dict(msg_timestamp=self.msg_timestamp,
                    msg_sender=self.msg_sender,
                    ack_timestamp=self.ack_timestamp,
                    ack_sender=self.ack_sender)

    def get_id(self):
        return self.ack_timestamp, self.ack_sender

    def get_acked_id(self):
        return self.msg_timestamp, self.msg_sender


class Payload:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_dict(self):
        return dict(key=self.key, value=self.value)


class Message:
    def __init__(self, sender, timestamp, order, payload):
        self.sender = sender
        self.timestamp = timestamp
        self.payload = payload
        self.order = order
        self.acked = False

    def to_dict(self):
        return dict(sender=self.sender,
                    timestamp=self.timestamp,
                    order=self.order,
                    payload=self.payload.to_dict())

    def get_id(self):
        return self.timestamp, self.sender

    def __lt__(self, other):
        return self.get_id() < other.get_id()
