from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Argon2id with recommended parameters for high security
# Memory: 64MB, Iterations: 3, Parallelism: 4 (RFC 9106)
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return ph.hash(password)

def verify_password(hashed: str, password: str) -> bool:
    """Verify a password against an Argon2id hash."""
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Catch-all for any other verification issues (e.g. malformed hash)
        return False

def check_needs_rehash(hashed: str) -> bool:
    """Check if a hash needs rehashing (e.g. if parameters changed)."""
    return ph.check_needs_rehash(hashed)
