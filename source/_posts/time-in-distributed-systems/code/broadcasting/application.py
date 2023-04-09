import json


class Application:
    """
    Application layer, in our case, a simple key-value store.
    """
    def __init__(self, data):
        self.data = data
        # For verification purposes, we keep track of the order in which messages were applied.
        self.order = []

    def process(self, msg_id, payload):
        self.order.append(msg_id)
        self.data[payload.key] = payload.value

    def dump(self):
        return json.dumps(dict(data=self.data, order=self.order))