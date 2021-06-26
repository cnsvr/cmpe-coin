from multiprocessing import Process
from CmpECoinNetwDispatcher import CmpECoinNetwDispatcher
from simple_node import CmpECoinSimpleNode
from validator import CmpECoinValidatorNode
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from CmpECoinWallet import CmpECoinWallet
from threading import Thread 
import time
meanTransactionInterDuration = 30
meanTransactionAmount = 10

def startSimple(wallet, PKsInNetwork):
  netwDispatcherAddress = 'localhost:5672'
  CmpECoinSimpleNode(wallet, meanTransactionInterDuration, meanTransactionAmount,  PKsInNetwork)

def startValidator():
  CmpECoinValidatorNode()

if __name__ == "__main__":
  simpleCount = 2
  validatorCount = 2

  simpleAddressesPublic = []
  simpleAddressesPrivate = []
  wallets = []

  for i in range(simpleCount):
    wallet = CmpECoinWallet()
    wallet.initWallet()

    simpleAddressesPublic.append(wallet.getPublicKey())
    simpleAddressesPrivate.append(wallet.getPrivateKey())
    wallets.append(wallet)

  dispatcherNode = CmpECoinNetwDispatcher(simpleAddressesPublic)
  print("dispatcher init")

  for i in range(simpleCount):
    simpleNode = Thread(target=startSimple, args=(wallets[i], simpleAddressesPublic, ))
    simpleNode.start()

  for i in range(validatorCount):
    vNode = Thread(target=startValidator)
    vNode.start()

  time.sleep(3)

  dispatcherNode.run()