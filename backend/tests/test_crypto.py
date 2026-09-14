from services.encryption import encrypt_data, decrypt_data
from services.shamir import split_secret, reconstruct_secret

original = b"CONFIDENTIAL QUESTION PAPER TEST"

encrypted, key, nonce = encrypt_data(original)
shares = split_secret(key, 3, 5)

recovered_key = reconstruct_secret([shares[0], shares[2], shares[4]])
decrypted = decrypt_data(encrypted, recovered_key, nonce)

assert decrypted == original
assert len(key) == 32
assert len(shares) == 5

print("AES-256 + Shamir 3-of-5 test PASSED")
