import time
from .qkd_protocol import QKDProtocol
from .random_generator import NumpyRandomGenerator, SecureRandomGenerator
from .bases import Bases
from .connection_role import ConnectionRole

class ConnectionAbort(Exception):
    pass


class SimpleBB84(QKDProtocol):
    bases_to_encode = [Bases.X, Bases.Z]
    random_generator = SecureRandomGenerator
    additional_qbits_factor = 10e-2
    
    def __init__(self, conn, debug=False):
        super().__init__(conn)
        self.debug = debug
    
    def get_random_bits(self, length):
        return list(self.random_generator.get_randomly_choosen_from([0, 1], length))
    
    def get_randomly_choosen_bases(self, length):
        return list(self.random_generator.get_randomly_choosen_from(self.bases_to_encode, length))
    
    def get_qbits_length_from_key_length(self, key_length):
        return int((4 + self.additional_qbits_factor) * key_length)
    
    def send_random_qubits(self, N, bits, bases):
        # encode and send qbits to the peer
        for i in range(N):
            q = self._conn.getQubit()
            bases[i].get_instance().encode(q, bits[i])
            self._conn.sendQubit(q)
    
    def get_bits_from_qubits(self, N, bases):
        bits = []
        for i in range(N):
            q = self._conn.recvQubit()
            bit = bases[i].get_instance().measure(q)
            bits.append(bit)
        
        return bits
    
    def check_errors(self,test_bits, peer_test_bits):
        # compute the error rate
        number_of_errors = len([i for i in range(len(test_bits)) if test_bits[i] != peer_test_bits[i]])
        if number_of_errors > 0:
            raise ConnectionAbort()
    
    def exchange_key(self, N, role):
        # generate the random bits and bases to encode them in
        bases = self.get_randomly_choosen_bases(N)
        
        self.log("bases have been chosen")
        
        if role is ConnectionRole.Sender:
            bits = self.get_random_bits(N)
            self.send_random_qubits(N, bits, bases)
            
            # Wait for the peer's acknowledgment
            self._conn.waitForAck()
        else:
            bits = self.get_bits_from_qubits(N, bases)
            self._conn.sendAck()
        
        self.log("random bits have been chosen")
        
        # exchange bases
        if role is ConnectionRole.Sender:
            self._conn.sendClassical([b.value for b in bases])
            peer_bases = [Bases(int(b)) for b in self._conn.recvClassical()]
        else:
            peer_bases = [Bases(int(b)) for b in self._conn.recvClassical()]
            self._conn.sendClassical([b.value for b in bases])
        
        self.log("bases have been exchanged")
        
        # compare bases and find common rounds
        common_rounds = [i for i in range(N) if bases[i] is peer_bases[i]]
        common_round_bases = [bases[i] for i in common_rounds]
        
        if len(common_rounds) < N/2:
            raise ConnectionAbort()
        
        if role is ConnectionRole.Sender:
            # choose a randome sample to test on and send to peer
            number_of_bits_to_test = int(len(common_rounds)/2)
            test_bit_indexes = self.random_generator.get_random_sample(common_rounds, number_of_bits_to_test)
            self._conn.sendClassical(test_bit_indexes)
        else:
            # receive test bit indexes
            test_bit_indexes = [int(b) for b in self._conn.recvClassical()]
        
        self.log("test bits have been exchanged")
        
        # exchange with the test bits
        test_bits = [bits[i] for i in test_bit_indexes]
        if role is ConnectionRole.Sender:
            self._conn.sendClassical(test_bits)
            peer_test_bits = [int(b) for b in self._conn.recvClassical()]
        else:
            peer_test_bits = [int(b) for b in self._conn.recvClassical()]
            self._conn.sendClassical(test_bits)
        
        self.check_errors(test_bits, peer_test_bits)
        
        key_bits = [bits[i] for i in common_rounds if i not in test_bit_indexes]

        self.log("common round where", len(common_rounds))
        self.log(len(test_bit_indexes), "of them used for tests")
        self.log("remaining key is", len(key_bits), "bits long")

        self.log("Simple key established")
        
        return key_bits
    
    def log(self, *args):
        if self.debug:
            print(*args)

if __name__ == '__main__':
    p = SimpleBB84()
