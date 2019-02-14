from .noisy_bb84 import NoisyBB84
from .simple_bb84 import SimpleBB84
from .connection_role import ConnectionRole
import random
import numpy as np


def Ext(x, r):
	"""
	F = {f_r: {0,1}^n → {0,1}^m, r ∈ {0,1}^d}
	Ext_F: {0,1}^n × {0,1}^d → {0,1}^m
	Ext_F(x,r) = f_r(x)
	Ext(x, r) = r*x^T
	param x: key to hash, {0,1}^n
	param r: will be chosen with uniform probability from the set of bit strings of length len(x)
	"""
	ext = np.array(x) * np.array(r)

	return list(ext)


class PrivacyAmpilfiedBB84(NoisyBB84):
    def __init__(self, conn, debug=False):
        super().__init__(conn, debug=debug)
    
    def exchange_key(self, N, role):
        remaining_bits = super().exchange_key(N, role)
        
        if role is ConnectionRole.Sender:
            r = self.random_generator.get_random_bits(len(remaining_bits))
            self.log("Length of random bits r is ", len(r), r)
            self._conn.sendClassical(list(r))
            self._conn.waitForAck()
            key = Ext(remaining_bits, r)
        else:
            r = list(self._conn.recvClassical())
            self._conn.sendAck()
            self.log("Length of random bits r is ", len(r), r)
            key = Ext(remaining_bits, r)
        
        return key
