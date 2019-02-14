class QKDProtocol:    
    def __init__(self, conn):
        self._conn = conn

    def exchange_keys(self, length):
        raise NotImplementedError()