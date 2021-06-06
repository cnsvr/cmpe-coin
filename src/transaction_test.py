import unittest
import hashlib
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from transaction import CmpETransaction

sk_A = SigningKey.generate(curve=SECP256k1)
pk_A = sk_A.verifying_key

sk_B = SigningKey.generate(curve=SECP256k1)
pk_B = sk_B.verifying_key


class TestTransaction(unittest.TestCase):
  
  def test_initialize_instance(self):
    '''
      Test that transaction instance is valid.
    '''
    transaction_instance =  CmpETransaction(pk_A, pk_B, 100, False)
    self.assertEqual(transaction_instance.fromAddress, pk_A)
    self.assertEqual(transaction_instance.toAddress, pk_B)
    self.assertEqual(transaction_instance.amount, 100)

  def test_calculateTransactionHash(self):
    '''
      Test that it can calculate hash.
    '''
    transaction_instance =  CmpETransaction(pk_A, pk_B, 200, False)
    string_block = "{}{}{}{}".format(transaction_instance.fromAddress, 
                                     transaction_instance.toAddress,
                                     transaction_instance.amount, 
                                     transaction_instance.timestamp)
    hash = hashlib.sha256(string_block.encode()).hexdigest()
    self.assertEqual(transaction_instance.hash, hash)

  
  def test_signTransaction(self):
    '''
      Test that it can sign signature
    '''
    transaction_instance =  CmpETransaction(pk_A, pk_B, 200, False)
    transaction_instance.signTransaction(sk_A)
    self.assertNotEqual(transaction_instance.signature, None)

  def test_isTransactionValid(self):
    '''
      Test that transaction is valid.
    '''
    transaction_instance =  CmpETransaction(pk_A, pk_B, 200, False)
    transaction_instance.signTransaction(sk_A)
    self.assertEqual(transaction_instance.isTransactionValid(), True)

  def test_invalid_transaction(self):
    '''
      Test that transaction is invalid.
    '''
    transaction_instance =  CmpETransaction(pk_A, pk_B, 200, False)
    transaction_instance.signTransaction(sk_A)

    # change amount of transaction
    transaction_instance.amount = 300
    validation = transaction_instance.isTransactionValid()
    
    self.assertEqual(validation, False)

if __name__ == '__main__':
    unittest.main()