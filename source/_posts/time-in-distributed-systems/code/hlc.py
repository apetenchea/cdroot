from collections import namedtuple
from datetime import datetime


Timestamp = namedtuple('Timestamp', ['physical', 'logical'])


class HLC:
    """
    Hybrid Logical Clock
    """
    def __init__(self):
        self._last_timestamp = Timestamp(0, 0)

    @staticmethod
    def get_physical_time():
        """
        Retrieve the current physical time.
        """
        return datetime.now().timestamp()

    def get_timestamp(self):
        """
        Generate a new timestamp.
        """
        physical = self.get_physical_time()
        if physical <= self._last_timestamp.physical:
            # Physical time stays the same,
            # but the logical component gets updated.
            physical = self._last_timestamp.physical
            logical = self._last_timestamp.logical + 1
        else:
            logical = 0
        self._last_timestamp = Timestamp(physical, logical)
        return self._last_timestamp

    def get_timestamp_and_adjust(self, received: Timestamp):
        """
        Adjust the local clock based on a received timestamp and return a new timestamp.
        """
        physical = max(self.get_physical_time(),
                       self._last_timestamp.physical,
                       received.physical)
        if physical == self._last_timestamp.physical:
            if physical == received.physical:
                # The last recorded timestamp and the received timestamp
                # have the same physical time, greater than the current physical time.
                logical = max(self._last_timestamp.logical, received.logical) + 1
            else:
                # The last recorded timestamp has a higher physical time
                # than the received timestamp.
                logical = self._last_timestamp.logical + 1
        else:
            if physical == received.physical:
                # The received timestamp has a higher physical time
                # than the last recorded timestamp.
                logical = received.logical + 1
            else:
                # The current physical time is higher than
                # both the last recorded timestamp and the received timestamp.
                logical = 0
        self._last_timestamp = Timestamp(physical, logical)
        return self._last_timestamp
