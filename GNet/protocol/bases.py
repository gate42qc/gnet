from enum import Enum

class Bases(Enum):
    X = 0  # |+>/|-> 
    Y = 1  # 
    Z = 2  # |0>/|1>
    H = 3  #
    HT = 4 # 
    
    def get_instance(self):
        if self is Bases.X:
            return XBasis()
        if self is Bases.Y:
            return YBasis()
        if self is Bases.Z:
            return ZBasis()
        if self is Bases.H:
            return HBasis()
        if self is Bases.HT:
            return HTBasis()

class Basis:
    def encode(self, qubit, bit):
        raise NotImplementedError()
    
    def measure(self, qubit):
        raise NotImplementedError()

class XBasis(Basis):
    def encode(self, qubit, bit):
        if bit:
            qubit.X()
        #qubit.H()
        pass
    
    def measure(self, qubit):
        #qubit.H()
        return qubit.measure()

class YBasis(Basis):
    def encode(self, qubit, bit):
        if bit:
            qubit.X()
        qubit.K()
    
    def measure(self, qubit):
        qubit.K()
        return qubit.measure()

class ZBasis(Basis):
    def encode(self, qubit, bit):
        if bit:
            qubit.X()
    
    def measure(self, qubit):
        return qubit.measure()

class HBasis(Basis):
    def encode(self, qubit, bit):
        if bit:
            qubit.X()
        qubit.rot_Y(256-16) # or 32
    
    def measure(self, qubit):
        qubit.rot_Y(16)
        return qubit.measure()

class HTBasis(Basis):
    def encode(self, qubit, bit):
        if bit:
            qubit.X()
        qubit.rot_Y(256-240)
    
    def measure(self, qubit):
        qubit.rot_Y(240)
        return qubit.measure()