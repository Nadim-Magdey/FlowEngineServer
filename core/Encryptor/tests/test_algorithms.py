import unittest
from unittest.mock import patch
from ..Algorithms import (
    CloverEncryptor,
    APGMastercardEncryptor,
    FirstDataEncryptor,
    CCAvenueEncryptor,
    CybersourceFlexV1Encryptor,
)
from Crypto.PublicKey import RSA

class TestEncryptors(unittest.TestCase):
    
    def test_clover_encryptor(self):
        card_data = {"c": "4111111111111111"}
        encryptor = CloverEncryptor(card_data=card_data, public_key_data={})
        # Mock fetch_public_key to avoid network call
        with patch.object(CloverEncryptor, 'fetch_public_key') as mock_key:
            key = RSA.generate(2048)
            mock_key.return_value = key
            result = encryptor.encrypt()
            self.assertIn("encrypted", result)
            self.assertIsInstance(result["encrypted"], str)

    def test_apg_mastercard_encryptor_payload(self):
        card_data = {"c": "4111111111111111", "v": "123", "m": "12", "y": "2030"}
        public_key_data = {"n": "00D0B8", "e": "010001"}  # dummy
        extra_data = {"sessionId": "sess123", "merchantId": "merch456"}
        encryptor = APGMastercardEncryptor(card_data=card_data, public_key_data=public_key_data, extra_data=extra_data)
        payload = encryptor._build_payload(extra_data["sessionId"], extra_data["merchantId"], card_data["c"], card_data["v"], card_data["m"], card_data["y"])
        self.assertIn("s=sess123", payload)
        self.assertIn("m=merch456", payload)

    def test_firstdata_encryptor(self):
        card_data = {"c": "4111111111111111", "v": "123", "m": "12", "y": "2030", "fl": "John Doe"}
        key = RSA.generate(2048)
        pk = key.publickey().export_key().decode()
        public_key_data = {"pk": pk}
        encryptor = FirstDataEncryptor(card_data=card_data, public_key_data=public_key_data)
        result = encryptor.encrypt()
        self.assertIn("encryptedData", result)
        self.assertIsInstance(result["encryptedData"], str)

    def test_ccavenue_encryptor(self):
        card_data = {"c": "4111111111111111", "v": "123", "m": "12", "y": "2030"}
        key = RSA.generate(2048)
        pk = key.publickey().export_key().decode()
        public_key_data = {"pk": pk}
        encryptor = CCAvenueEncryptor(card_data=card_data, public_key_data=public_key_data)
        result = encryptor.encrypt()
        self.assertTrue(all(isinstance(v, str) for v in result.values()))

    def test_cybersource_flex_v1_encryptor(self):
        card_data = {"c": "4111111111111111"}
        key = RSA.generate(2048)
        pk = key.publickey().export_key().decode()
        public_key_data = {"pk": pk}
        encryptor = CybersourceFlexV1Encryptor(card_data=card_data, public_key_data=public_key_data)
        result = encryptor.encrypt()
        self.assertIn("encryptedData", result)
        self.assertIsInstance(result["encryptedData"], str)

if __name__ == "__main__":
    unittest.main()
