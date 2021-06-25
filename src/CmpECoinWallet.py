from ecdsa import SigningKey, VerifyingKey
import ecdsa

class CmpECoinWallet:

	def __init__(self):
		self.currentBalance = None
		self.privateKey = None
		self.publicKey = None

	def initWallet(self):
		self.currentBalance = 0
		self.privateKey = SigningKey.generate(curve=ecdsa.SECP256k1)
		self.publicKey = self.privateKey.verifying_key

	def getPublicKey(self):
		return self.publicKey

	def getPrivateKey(self):
		return self.privateKey

	def getCurrentBalance(self):
		return self.currentBalance

	def setCurrentBalance(self, current_balance):
		self.currentBalance = current_balance
