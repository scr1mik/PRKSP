import hashlib
import hmac
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        120_000,
    ).hex()
    return f"{password_salt}${password_hash}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, expected_hash = stored_password.split("$", maxsplit=1)
    except ValueError:
        return False

    actual_hash = hash_password(password, salt).split("$", maxsplit=1)[1]
    return hmac.compare_digest(actual_hash, expected_hash)


def create_session_id() -> str:
    return secrets.token_urlsafe(32)
