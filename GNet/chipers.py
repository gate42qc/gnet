import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

class QChiper(object):
    def __init__(self, key):
        self.key = key
    
    def encrypt(self, plaintext):
        aes = AES.new(self.key, AES.MODE_CFB)
        nonce = aes.nonce
        ciphertext, tag = aes.encrypt_and_digest(plaintext)
        return (nonce, ciphertext, tag)
        #return plaintext

    def decrypt(self, message):
        nonce, ciphertext, tag = message
        aes = AES.new(self.key, AES.MODE_CFB, nonce)
        plaintext = aes.decrypt(ciphertext)
        aes.verify(tag)
        return plaintext
        #return message

class AESCipher(object):

    def __init__(self, key): 
        self.bs = 32
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return bytes(base64.b64encode(iv + cipher.encrypt(raw)))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

