from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Optional


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt_bytes = salt or os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 200_000)
    return f"{salt_bytes.hex()}${derived_key.hex()}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        salt_hex, _hash_hex = stored_value.split("$", 1)
    except ValueError:
        return False
    expected = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(expected, stored_value)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
