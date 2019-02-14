from bases import Bases
from .simple_bb84 import SimpleBB84


class SixStatesProtocol(SimpleBB84):
    bases_to_encode = [Bases.Z, Bases.X, Bases.Y]
    
    def __init__(self, conn, debug=False):
        super().__init__(conn, debug=debug)
    
