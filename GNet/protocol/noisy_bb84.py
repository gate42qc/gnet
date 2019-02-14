import numpy as np
import random
from .simple_bb84 import SimpleBB84, ConnectionAbort
from .connection_role import ConnectionRole


H_Hamming =  np.array([[1, 0, 1, 0, 1, 0, 1],
                   [0, 1, 1, 0, 0, 1, 1],
                   [0, 0, 0, 1, 1, 1, 1]])

H_Golay = np.array([[1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                    [1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                    [1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    [1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                    [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]])


def trace_dist(rho0, rho1):
    # Compute the difference operator and its eigenvalues
    A = rho0 - rho1
    eigA = np.linalg.eig(A)[0]
    #print("eigenvalues of rho0-rho1", eigA)

        # the optimal distinguishing measurement 
        # is given by the projectors on the positive
        # and negative eigenspaces of A. Chiefly the trace 
        # distance could be obtained from trace(MA) where M
        # is a projector on the positive eigenspace of A. 
        # To compute this, all we have to do is hence to compute
        # the sum of positive eigenvalues of A.

    s = 0
    for j in range(len(eigA)):
        if(eigA[j] > 0):
            s = s + eigA[j]
    
    return s


def cross_entropy(delta):
    h = -delta * np.log2(delta + 10e-4) - (1 - delta) * np.log2(1 - delta)
    
    return h


# rho0 = 1/2* |0><0| + 1/2 * |+><+|
rho0 = 1/2 * np.array([[1, 0],[0, 0]]) + 1/2 * np.array([[1, 1],[1, 1]])/2
# rho1 = 1/2* |1><1| + 1/2 * |-><-|
rho1 = 1/2 * np.array([[0, 0],[0, 1]]) + 1/2 * np.array([[1, -1],[-1, 1]])/2
p_guess = 1/2 + 1/2 * trace_dist(rho0, rho1)
MIN_ENTROPY = -np.log2(p_guess)


## encoder
def get_syndrome(v):
    """ Input:
     ------
     H - k x n parity check matrix
     v - length n vector
     Output: syndrome of v with parity check matrix H
    """
    H = H_Golay
    v = np.array(v)
    row, col = H.shape
    to_pad = col-len(v)
    if len(v) % col != 0:
        raise ValueError("invalid v shape")
    if len(v) > col:
        return np.concatenate((get_syndrome(v[:col]), get_syndrome(v[col:])))
    
    v = v[:, np.newaxis]
    s = H.dot(v) % 2
    return s.reshape(len(s), )


def decode(Ca, Xb):
    H = H_Golay
    if len(Ca) > 11:
        return np.concatenate((decode(Ca[:11], Xb[:23]), decode(Ca[11:], Xb[23:])))
    Ca = np.array(Ca)
    Cb = get_syndrome(Xb)
    Cs = (Ca + Cb) % 2
    estimator_dict = dict_golay()
    S_hat = estimator_dict[tuple(Cs)]
    S_hat = S_hat.reshape(len(S_hat), )
    Xa_hat = (Xb + S_hat) % 2
    
    return Xa_hat


def dict_hamming():
    dict_Hamming = {}
    zero = 0*eVec(7,1)
    s = tuple(0*eVec(3,1))
    dict_Hamming[s] = zero
    for i in range(7):
        vi = eVec(7, i)
        s = tuple(get_syndrome(H_Hamming, vi))
        dict_Hamming[s] = vi
    
    return dict_Hamming


def dict_golay(length=23):
    dict_Golay = {}
    zero = eVec(length, 0)*0
    s = get_syndrome(zero)
    s = tuple(s)
    dict_Golay[s] = zero

    for i in range(length):
        vi = eVec(length, i)
        s = tuple(get_syndrome(vi))
        dict_Golay[s] = vi    
        for j in range(i+1, length):
            vj = (vi + eVec(length, j))
            s = tuple(get_syndrome(vj))
            dict_Golay[s] = vj
            for k in range(j+1, length):
                vk = (vj + eVec(length, k))
                s = tuple(get_syndrome(vk))
                dict_Golay[s] = vk
    return dict_Golay


def eVec(n,j):
    """
    creates vector in the standard basis
    """
    v = np.zeros((n,), dtype=int)
    v[j] = 1
    
    return v


def regularize(vector, size=23):
    vector = list(vector)
    if len(vector) % size == 0:
        to_pad = 0
    else:
        to_pad = size - (len(vector) % size)
    return vector + [0]*to_pad


class NoisyBB84(SimpleBB84):
    def __init__(self, conn, debug=False):
        super().__init__(conn, debug=debug)
    
    def check_errors(self, test_bits, peer_test_bits):
        number_of_errors = len([i for i in range(len(test_bits)) if test_bits[i] != peer_test_bits[i]])
        delta = number_of_errors/len(test_bits)
        self.log("Error rate is:", delta)
        # check what is Eve's best guessing probability
        h = cross_entropy(delta)

        if MIN_ENTROPY >= len(test_bits)*(1-h):
            raise ConnectionAbort
    
    def exchange_key(self, N, role):
        remaining_bits = super().exchange_key(N, role)
        self.log("Remaining bits are of", len(remaining_bits), "length")
        
        remaining_bits = regularize(remaining_bits)
        self.log("Reminig bits before reconcilation, ", remaining_bits, "with length: ", len(remaining_bits))
        if role is ConnectionRole.Sender:
            sender_syndrome = list(get_syndrome(remaining_bits))
            self._conn.sendClassical(sender_syndrome)
        else:
            sender_syndrome = list(self._conn.recvClassical())
            remaining_bits = decode(sender_syndrome, remaining_bits)

        self.log("Noisy key established, with length: ", len(remaining_bits))
        
        return list(remaining_bits)
