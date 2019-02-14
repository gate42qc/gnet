import logging
from SimulaQron.cqc.pythonLib.cqc import CQCConnection

class GCQCConnection(CQCConnection):
    
    def sendClassical(self, name, msg, close_after=True):
        if name not in self._classicalConn:
            self.openClassicalChannel(name)

        # Added support for bytes and bytesarray message types
        isDecodable = False
        try:
            tmp = msg.decode()
            isDecodable = True
        except AttributeError:
            isDecodable = False

        if isDecodable:
            to_send = msg
        else:
            try:
                to_send = [int(msg)]
            except TypeError:
                to_send = msg
            to_send = bytes(to_send)
        logging.debug("App {}: Sending classical message {} to {}".format(self.name, to_send, name))
        self._classicalConn[name].send(to_send)
        logging.debug("App {}: Classical message {} to {} sent".format(self.name, to_send, name))
        if close_after:
            self.closeClassicalChannel(name)