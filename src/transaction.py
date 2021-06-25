from datetime import datetime
import time
import logging, coloredlogs
import hashlib
import json
from ecdsa import SigningKey, VerifyingKey

MAX_REWARD = 1 # CmpECoin

# export COLOREDLOGS_LEVEL_STYLES='info=35;error=124'

coloredlogs.install()

class CmpETransaction:  
  def __init__(self, fromAddress, toAddress, amount, log = True):

    # If the fromAddress is null, it is called a reward transaction and amount can't be greater than MAX_REWARD CmpECoin.
    if fromAddress == None and amount > MAX_REWARD:
      raise ValueError("Amount can't be greater than MAX_REWARD (1 CmpECoin)")
    
    if fromAddress and not isinstance(fromAddress, VerifyingKey):
      raise TypeError("fromAddress has to be an instance of VerifyingKey or None")

    if not isinstance(toAddress, VerifyingKey):
      raise TypeError("toAddress has to be an instance of VerifyingKey")
    
    if not amount > 0:
      raise ValueError("Amount has to be greater than 0")

    self.fromAddress = fromAddress
    self.toAddress = toAddress
    self.amount = amount
    self.timestamp = time.time()
    self.hash = self.__calculateTransactionHash()
    self.signature = None
    if (log):
      logging.info("A transaction({}) of {} CmpECoin created from {} to {} at {}".format(self.hash,
                                                                                       amount,
                                                                                       fromAddress.to_string().hex() if fromAddress else fromAddress,
                                                                                       toAddress.to_string().hex(),
                                                                                       datetime.fromtimestamp(self.timestamp)))
  
  def __calculateTransactionHash(self):
    string_block = "{}{}{}{}".format(self.fromAddress, self.toAddress, self.amount, self.timestamp)
    return hashlib.sha256(string_block.encode()).hexdigest()

  def signTransaction(self, secretKey):
    if not isinstance(secretKey, SigningKey):
      logging.error("Secret Key is not instance of SigningKey. You can't sign the transaction")
      return False
    else:
      self.signature = secretKey.sign(self.hash.encode('utf-8'))
      return True

  def isTransactionValid(self):
    isTransactionValid = True
    # If the fromAddress is None, no need to signature
    if not self.fromAddress:
      return isTransactionValid
    else:
      # Recalculates the hash to detect any changes of properties
      self.hash = self.__calculateTransactionHash()
      try:
        isTransactionValid = self.fromAddress.verify(self.signature, self.hash.encode('utf-8'))
      except:
        # add log here
        isTransactionValid = False

    return isTransactionValid

  def __repr__(self):
    return self.toJSON()

  def toJSON(self):
    t = {}
    t['fromAddress'] = self.fromAddress.to_string().hex()
    t['toAddress'] = self.toAddress.to_string().hex()
    t['amount'] = self.amount
    t['timestamp'] = self.timestamp
    t['hash'] = self.hash
    t['signature'] = self.signature.hex()
    return json.dumps(t, default=lambda o: o.__dict__, indent=4)
