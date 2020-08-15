from .protocol import PrivacyAmpilfiedBB84, NoisyBB84, SimpleBB84, ConnectionRole, ConnectionAbort
from .chipers import QChiper, AESCipher
from .gcqc import GCQCConnection
from cqc.pythonLib import qubit


class UnableToConnect(Exception):
    pass


def bits_to_num(bits):
    return sum([2**i for i, b in enumerate(bits) if b])


def key_to_bytes(key):
    return bytes([bits_to_num(key[i:i+8]) for i in range(len(key)//8)])


class GNetConnection():
    max_retries = 10
    key_length = 5
    
    def __init__(self, name, peer, debug=True):
        self._cqc_conn = GCQCConnection(name)
        self._peer = peer
        self.protocol = PrivacyAmpilfiedBB84(self, debug=debug)
        self.debug = debug
    
    def __enter__(self):
        self._cqc_conn.__enter__()
        return self
    
    def __exit__(self, *args):
        self._cqc_conn.__exit__(*args)
    
    def recvQubit(self):
        return self._cqc_conn.recvQubit()
    
    def sendQubit(self, qubit):
        return self._cqc_conn.sendQubit(qubit, self._peer)
    
    def sendAck(self):
        self._cqc_conn.sendClassical(self._peer, 1, close_after=False)
    
    def waitForAck(self):
        self._cqc_conn.recvClassical(close_after=False)
    
    def recvClassical(self):
        return self._cqc_conn.recvClassical(close_after=False)
    
    def sendClassical(self, data):
        return self._cqc_conn.sendClassical(self._peer, data, close_after=False)
    
    def getQubit(self):
        return qubit(self._cqc_conn)
    
    def sendEncripted(self, message):
        if message == "":
            self.sendClassical("close".encode("utf-8"))
            self.info("Closing the connection")
            self.waitForAck()
            return
        else:
            self.sendClassical("start".encode("utf-8"))
        
        self.info("Trying to send message", message, "to", self._peer)
        # number of the qbits to use
        N = self.protocol.get_qbits_length_from_key_length(self.key_length)
        
        self.log("establishing a key with ", N, " qubits")
        
        retries = 0
        while self.max_retries > retries:
            try:
                key = self.protocol.exchange_key(N, ConnectionRole.Sender)
                break
            except ConnectionAbort:
                self.log("couldn't establish a key, trying again")
                pass
            retries += 1
        else:
            raise UnableToConnect()
        self.log("key established", key)
        
        ciper = AESCipher(key_to_bytes(key))
        cipertext = ciper.encrypt(message)
        self.log("sending cipertext", cipertext)
        self.log("with message", message)
        self.sendClassical(cipertext)
        
    def receiveEncripted(self):
        self.info("Waiting for message from", self._peer)
        command = self.recvClassical().decode("utf-8")
        if command == "close":
            self.sendAck()
            self.info(self._peer, "closed the connection.")
            return
        
        # number of the qbits to use
        N = self.protocol.get_qbits_length_from_key_length(self.key_length)
        
        self.log("establishing a key with ", N, " qubits")
        
        retries = 0
        while self.max_retries > retries:
            try:
                key = self.protocol.exchange_key(N, ConnectionRole.Receiver)
                break
            except ConnectionAbort:
                self.log("couldn't establish a key, trying again")
                pass
            retries += 1
        else:
            raise UnableToConnect()
        
        self.log("key established", key)

        ciper = AESCipher(key_to_bytes(key))
        cipertext = (self.recvClassical())
        message = ciper.decrypt(cipertext)
        self.log("cipertext received ", cipertext)
        self.log("message was ", message)
        
        return message
    
    def log(self, *args):
        if self.debug:
            print(*args)
    
    def info(self, *args):
        print(*args)
