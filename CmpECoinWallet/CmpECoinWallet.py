#!/usr/bin/env python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class CmpECoinWallet:

	def __init__(self):
		self.currentBalance = None
		self.privateKey = None
		self.publicKey = None

	def initWallet(self):
		self.currentBalance = 0
		self.privateKey = rsa.generate_private_key(public_exponent=65537,key_size=2048,backend=default_backend())
		self.publicKey = private_key.public_key()

	def getPublicKey(self):
		return self.publicKey

	def getPrivateKey(self):
		return self.privateKey

	def getCurrentBalance(self):
		return self.currentBalance

	def setCurrentBalance(self, current_balance):
		self.currentBalance = current_balance
