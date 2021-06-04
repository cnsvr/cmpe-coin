from datetime import datetime
import time
import logging
import hashlib
from ecdsa import SigningKey, VerifyingKey

# make it globally
logging.basicConfig(level=logging.INFO)

class CmpETransaction:
  def __init__(self, fromAddress, toAddress, amount):
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
  
  def __calculateTransactionHash(self):
    string_block = "{}{}{}{}".format(self.fromAddress, self.toAddress, self.amount, self.timestamp)
    return hashlib.sha256(string_block.encode()).hexdigest()

  def signTransaction(self, secretKey):
    if not isinstance(secretKey, SigningKey):
      logging.info("Secret Key is not instance of SigningKey. You can't sign the transaction")
      return
    else:
      self.signature = secretKey.sign(self.hash.encode('utf-8'))

  def isTransactionValid(self):
    isTransactionValid = True
    if not isinstance(self.fromAddress, VerifyingKey):
      logging.info("Public Key is not instance of VerifyingKey. FromAddress must be valid Public Key")
      return False
    else:
      # Recalculates the hash to detect any changes of properties
      self.hash = self.__calculateTransactionHash()
      try:
        isTransactionValid = self.fromAddress.verify(self.signature, self.hash.encode('utf-8'))
      except:
        isTransactionValid = False

    return isTransactionValid



'''
# SECP256k1 is the Bitcoin elliptic curve
sk = SigningKey.generate(curve=SECP256k1)
pk = sk.verifying_key
print(type (pk))
print(pk.to_string())
transaction = CmpETransaction("A","B",100)
signature = sk.sign(transaction.hash.encode('utf-8'))
print(pk.verify(signature, transaction.hash.encode('utf-8')))
'''


'''
private_key = SigningKey.generate(curve=SECP256k1)
 string_private_key = private_key.to_string()
 SigningKey.from_string(string_private_key, curve=SECP256k1)
'''