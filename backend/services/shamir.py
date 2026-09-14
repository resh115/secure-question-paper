import secrets

# A 521-bit prime field is comfortably larger than a 256-bit AES key.
PRIME = 2**521 - 1
THRESHOLD = 3
TOTAL_SHARES = 5
AES_KEY_LENGTH = 32

def _eval_polynomial(coefficients, x):
    result = 0
    for coefficient in reversed(coefficients):
        result = (result * x + coefficient) % PRIME
    return result

def split_secret(secret: bytes, threshold=THRESHOLD, shares=TOTAL_SHARES):
    if threshold > shares:
        raise ValueError("Threshold cannot be greater than number of shares.")
    if threshold < 2:
        raise ValueError("Threshold must be at least 2.")
    secret_int = int.from_bytes(secret, "big")
    if secret_int >= PRIME:
        raise ValueError("Secret is too large for the selected field.")

    coefficients = [secret_int]
    coefficients.extend(secrets.randbelow(PRIME) for _ in range(threshold - 1))
    return [(x, _eval_polynomial(coefficients, x)) for x in range(1, shares + 1)]

def reconstruct_secret(shares, secret_length=AES_KEY_LENGTH):
    if len(shares) < THRESHOLD:
        raise ValueError(f"At least {THRESHOLD} shares are required.")

    secret_int = 0
    for i, (x_i, y_i) in enumerate(shares):
        numerator = 1
        denominator = 1
        for j, (x_j, _) in enumerate(shares):
            if i != j:
                numerator = (numerator * (-x_j)) % PRIME
                denominator = (denominator * (x_i - x_j)) % PRIME
        lagrange = numerator * pow(denominator, -1, PRIME) % PRIME
        secret_int = (secret_int + y_i * lagrange) % PRIME

    try:
        return secret_int.to_bytes(secret_length, "big")
    except OverflowError as exc:
        raise ValueError("Reconstructed secret does not fit expected length.") from exc

def serialize_share(share):
    x, y = share
    return f"{x}:{y}"

def deserialize_share(value):
    x, y = value.split(":", 1)
    return int(x), int(y)
