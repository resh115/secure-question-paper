import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(data: bytes):
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    return ciphertext, key, nonce

def decrypt_data(ciphertext: bytes, key: bytes, nonce: bytes):
    return AESGCM(key).decrypt(nonce, ciphertext, None)
