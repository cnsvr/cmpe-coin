from multiprocessing import Process
from CmpECoinNetwDispatcher import CmpECoinNetwDispatcher
from simple_node import CmpECoinSimpleNode
from validator import CmpECoinValidatorNode
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from CmpECoinWallet import CmpECoinWallet
from threading import Thread 
import ecdsa
import time
import sys


PKs= ['20bf96d77dd5bfbdff30b099e9c5bbfcd49888008aee47b4e6d91ef95a1b59a6', 'b4521501b02417c2bf8036b3993c5728ca08e6adf40f2fd895fecc30083da7fd', 'b5070a4802bc7f572fcc9dfa5cb7c85c0e775e54b090272415715e4156fa7bcb']
Publics = ['093bd529134dfb8d23f790b0ee86c5ddceb5799701331c46ea767daab1a4b09b4478c1b05e34f7e885345e83c0222fe0883ca6ab2621447c34472d0416c0eb7c', '280ce949f4b465987b8e3aa69ba4bab7dbc0f8792f237fb097322d4d8174f875e37490e81dd864499ae46cf869e338b3b35839d7946575cb8417b935dceefba7', '8be6ff238a7989d72d543bdf07df7132604fb95e7842f81e8ca140cdc8bbe247054ec61caa6e88075c5a200d0fd1b7394c3cad0dd2c1d062babdf01ec0d718da']
simpleAddressesPublic = []

for i in range(0,3):
    skk = SigningKey.from_string(bytes.fromhex(PKs[i]), curve=ecdsa.SECP256k1)
    simpleAddressesPublic.append(skk.verifying_key)

dispatcherNode = CmpECoinNetwDispatcher(simpleAddressesPublic)
dispatcherNode.run()