from datetime import datetime
import time
import logging
import hashlib
import ecdsa

# make it globally
logging.basicConfig(level=logging.INFO)

class CmpETranscation:
  def __init__(self, fromAddress: str, toAddress: str, amount: int):
    self.fromAddress = fromAddress
    self.toAddress = toAddress
    self.amount = amount
    self.timestamp = time.time()
    self.hash = self.__calculateTransactionHash()
    self.signature = None
    logging.info("A transaction({}) of {} CmpECoin created from {} to {} at {}".format(self.hash,
                                                                                       amount,
                                                                                       fromAddress,
                                                                                       toAddress,
                                                                                       datetime.fromtimestamp(self.timestamp)))
  
  def __calculateTransactionHash(self) -> str:
    string_block = "{}{}{}{}".format(self.fromAddress, self.toAddress, self.amount, self.timestamp)
    return hashlib.sha256(string_block.encode()).hexdigest()

  def signTransaction(self, secretKey: str):
    pass

  def isTransactionValid(self):
    return True


'''
# SECP256k1 is the Bitcoin elliptic curve
sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
vk = sk.get_verifying_key()
sig = sk.sign(b"message")
print(vk.verify(sig, b"message")) # True
'''