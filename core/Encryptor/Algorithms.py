import base64
import json
import pathlib
import urllib.parse
from datetime import datetime
from typing import Optional
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5, AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1, SHA256
from Crypto.Util.Padding import pad
from Crypto.Util.number import bytes_to_long
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.backends import default_backend
import requests
from Crypto.Hash import SHA256 as SHA256aa
import subprocess

class BaseEncryptor:
    method_name: str = "Base"
    
    def __init__(self, card_data: dict, public_key_data: dict, extra_data: Optional[dict] = None):
        self.card_data = card_data or {}
        self.public_key_data = public_key_data or {}
        self.extra_data = extra_data or {}

    def validate_fields(self, required_fields: list):
        missing = [f for f in required_fields if not self._get_field_value(f)]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
    def _get_field_value(self, field: str):
        parts = field.split('.')
        data = {'cardData': self.card_data, 'publicKey': self.public_key_data, 'extra': self.extra_data}
        val = data.get(parts[0])
        if val is None:
            return None
        for p in parts[1:]:
            val = val.get(p) if val else None
        return val

    def encrypt(self):
        raise NotImplementedError("Encrypt method must be implemented in subclass.")


class CloverEncryptor(BaseEncryptor):
    method_name = "Clover"
    _cached_key = None
    _cached_timestamp = None

    def fetch_public_key(self):
        if self._cached_key and self._cached_timestamp and (datetime.utcnow() - self._cached_timestamp).total_seconds() < 24*3600:
            return self._cached_key
        
        KEY_URL = "https://checkout.clover.com/assets/keys.json"
        resp = requests.get(KEY_URL)
        key_b64 = resp.json()["TA_PUBLIC_KEY_PROD"]
        key_bytes = base64.b64decode(key_b64)
        modulus = bytes_to_long(key_bytes[:256])
        exponent = bytes_to_long(key_bytes[256:])
        public_key = RSA.construct((modulus, exponent))
        self._cached_key = public_key
        self._cached_timestamp = datetime.utcnow()
        return public_key

    def encrypt_card_number(self, prefix_id="00000000"):
        pan = self.card_data.get("c")
        if not pan:
            raise ValueError("Missing card number 'c'")
        public_key = self.fetch_public_key()
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA1)
        encrypted = cipher.encrypt(f"{prefix_id}{pan}".encode())
        return base64.b64encode(encrypted).decode()

    def encrypt(self):
        return {"encrypted": self.encrypt_card_number()}


class APGMastercardEncryptor(BaseEncryptor):
    method_name = "APGMastercard"

    @staticmethod
    def _trim(s):
        return s.strip() if isinstance(s, str) else s

    @staticmethod
    def _k(prefix: str, value) -> str:
        if value is None or value == "":
            return ""
        return prefix + urllib.parse.quote_plus(str(value))

    def _build_payload(self, session_id, merchant_id, card_number, cvv, month, year, preferred_card_type=None):
        session_id = self._trim(session_id)
        merchant_id = self._trim(merchant_id)
        card_number = self._trim(card_number)
        cvv = self._trim(cvv)
        month = self._trim(month)
        year = self._trim(year)
        preferred_card_type = self._trim(preferred_card_type) if preferred_card_type else None
        
        d = ""
        if session_id:
            d = "s=" + urllib.parse.quote_plus(session_id) + "&"
        d += "m=" + urllib.parse.quote_plus(merchant_id)
        d += self._k("&cn=", card_number)
        d += self._k("&csc=", cvv)
        d += self._k("&xm=", month)
        d += self._k("&xy=", year)
        if preferred_card_type:
            d += self._k("&pct=", preferred_card_type)
        return d

    @staticmethod
    def _rsa_public_pem_from_hex(modulus_hex: str, exponent_hex: str) -> str:
        n_int = int(modulus_hex.replace(" ", ""), 16)
        e_int = int(exponent_hex.replace(" ", ""), 16)
        pub_numbers = rsa.RSAPublicNumbers(e_int, n_int)
        pub_key = pub_numbers.public_key(default_backend())
        return pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def encrypt(self):
        card_block = self.card_data
        pub_block = self.public_key_data

        session_id = self.extra_data.get("sessionId")
        merchant_id = self.extra_data.get("merchantId")

        c = card_block.get("c")
        v = card_block.get("v")
        m = card_block.get("m")
        y = card_block.get("y")

        modulus_hex = pub_block.get("n")
        exponent_hex = pub_block.get("e")
        preferred_card_type = card_block.get("pct")

        self.validate_fields([
            "cardData.c", "cardData.v", "cardData.m", "cardData.y",
            "publicKey.n", "publicKey.e", "extra.sessionId", "extra.merchantId"
        ])

        payload = self._build_payload(session_id, merchant_id, c, v, m, y, preferred_card_type)
        pem = self._rsa_public_pem_from_hex(modulus_hex, exponent_hex)
        pub_key = serialization.load_pem_public_key(pem.encode(), backend=default_backend())
        ciphertext = pub_key.encrypt(payload.encode(), asym_padding.PKCS1v15())
        return {"payload": payload, "d": base64.b64encode(ciphertext).decode()}


class FirstDataEncryptor(BaseEncryptor):
    method_name = "FirstData"

    def encrypt(self):
        c = self.card_data.get("c")
        v = self.card_data.get("v")
        m = self.card_data.get("m")
        y = self.card_data.get("y")
        fl = self.card_data.get("fl")
        pk = self.public_key_data.get("pk")

        self.validate_fields(["cardData.c", "cardData.v", "cardData.m", "cardData.y", "cardData.fl", "publicKey.pk"])

        card_data = {"card": c, "cvv": v, "exp": f"{m}/{y[2:4]}", "name": fl}
        public_key = RSA.import_key(base64.b64decode(pk) if "BEGIN" not in pk else pk)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_data = cipher.encrypt(json.dumps(card_data).encode())
        return {"encryptedData": base64.b64encode(encrypted_data).decode()}


class CCAvenueEncryptor(BaseEncryptor):
    method_name = "CCAvenue"

    def encrypt_ccavenue(self, data):
        pk = self.public_key_data.get("pk")
        if "-----BEGIN PUBLIC KEY-----" not in pk:
            pk = f"-----BEGIN PUBLIC KEY-----\n{pk}\n-----END PUBLIC KEY-----"
        public_key = RSA.import_key(pk)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    def encrypt(self):
        c = self.card_data.get("c")
        v = self.card_data.get("v")
        m = self.card_data.get("m")
        y = self.card_data.get("y")
        self.validate_fields(["cardData.c", "cardData.v", "cardData.m", "cardData.y", "publicKey.pk"])
        return {
            "c": self.encrypt_ccavenue(c),
            "v": self.encrypt_ccavenue(v),
            "m": self.encrypt_ccavenue(m),
            "y": self.encrypt_ccavenue(y)
        }


class CybersourceFlexV1Encryptor(BaseEncryptor):
    method_name = "CybersourceFlex-v1"

    def encrypt(self):
        c = self.card_data.get("c")
        pk = self.public_key_data.get("pk")
        self.validate_fields(["cardData.c", "publicKey.pk"])
        key = RSA.import_key(pk)
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        encrypted = cipher.encrypt(c.encode())
        return {"encryptedData": base64.b64encode(encrypted).decode()}


class CybersourceFlexV2Encryptor(BaseEncryptor):
    method_name = "CybersourceFlexV2"

    NODE_SCRIPT_PATH = pathlib.Path(__file__).parent / "js" / "cyberSourceFlexv2.js"

    def encrypt(self) -> dict:
        self.validate_fields([
            "cardData.number",
            "cardData.securityCode",
            "cardData.expirationMonth",
            "cardData.expirationYear",
            "cardData.type",
            "publicKey.context",
        ])

        # 🔑 context MUST be JSON
        context_obj = self._get_field_value("publicKey.context")
        context_json = json.dumps(context_obj)

        cmd = [
            "node",
            self.NODE_SCRIPT_PATH,
            context_json,
            self._get_field_value("cardData.number"),
            self._get_field_value("cardData.securityCode"),
            self._get_field_value("cardData.expirationMonth"),
            self._get_field_value("cardData.expirationYear"),
            self._get_field_value("cardData.type"),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"CybersourceFlexV2 encryption failed: {result.stderr.strip()}"
            )

        return json.loads(result.stdout)



class AdyenV0125Encryptor(BaseEncryptor):
    method_name = "Adyen-v0.1.25"

    def encrypt(self):
        # Pure Python AESCCM example (matches Adyen v0.1.25)
        c = self.card_data.get("c")
        pk = self.public_key_data.get("pk")
        nonce = b"0123456789ab"  # Normally random 12 bytes ( should be randomly generated)
        self.validate_fields(["cardData.c", "publicKey.pk"])
        key = base64.b64decode(pk)
        aesccm = AESCCM(key, tag_length=16)
        encrypted = aesccm.encrypt(nonce, c.encode(), None)

        return {"encryptedData": base64.b64encode(encrypted).decode(), "nonce": base64.b64encode(nonce).decode()}


class AdyenV441Encryptor(BaseEncryptor):

    method_name = "Adyen-v4.4.1"
    
    def encrypt(self):
        # AESCCM with additional fields
        c = self.card_data.get("c")
        pk = self.public_key_data.get("pk")
        nonce = b"0123456789cd"  # Normally random 12 bytes
        self.validate_fields(["cardData.c", "publicKey.pk"])
        key = base64.b64decode(pk)
        aesccm = AESCCM(key, tag_length=16)
        encrypted = aesccm.encrypt(nonce, c.encode(), None)
        return {"encryptedData": base64.b64encode(encrypted).decode(), "nonce": base64.b64encode(nonce).decode()}


class YahooSBEncryptor(BaseEncryptor):
    method_name = "YahooSB"
    
    def encrypt(self):
        # YahooSB encryption in JS uses Node crypto, here we mimic with AES ECB + base64
        c = self.card_data.get("c")
        pk = self.public_key_data.get("pk")
        self.validate_fields(["cardData.c", "publicKey.pk"])
        key = base64.b64decode(pk)[:16]  # truncate to 16 bytes
        cipher = AES.new(key, AES.MODE_ECB)
        padded = pad(c.encode(), 16)
        encrypted = cipher.encrypt(padded)
        return {"encryptedData": base64.b64encode(encrypted).decode()}


class PIEv1Encryptor(BaseEncryptor):
    method_name = "PIEv1"

    def encrypt(self):
        c = self.card_data.get("c")
        self.validate_fields(["cardData.c"])
        # Simple mock example, actual PIEv1 uses HMAC + AES in JS
        return {"encryptedData": base64.b64encode(c[::-1].encode()).decode()}


class CommerceV3Encryptor(BaseEncryptor):
    method_name = "CommerceV3"

    def encrypt(self):
        c = self.card_data.get("c")
        self.validate_fields(["cardData.c"])
        # Mock: reverse + base64 as placeholder
        return {"encryptedData": base64.b64encode(c[::-1].encode()).decode()}


class MockEncryptor(BaseEncryptor):
    method_name = "MockEncryptor"
    
    def encrypt(self):
        # For testing / placeholder
        return {"encryptedData": base64.b64encode(json.dumps(self.card_data).encode()).decode()}
    
if __name__ == "__main__":
    
    encryptor = CloverEncryptor(card_data={"c": "4111111111111111"}, public_key_data={})
    result = encryptor.encrypt()
    print(result)

    