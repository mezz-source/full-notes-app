import hashlib
import hmac
import base64

async def hash_password(password: str, salt: str | None = None) -> str:
    """Creates a new hash for the provided password.
    
    Arguments:
        password (str): The password to hash
        salt (str): The salt for the provided hash. Creates salt by default

    Returns:
        hashed_password (str): Returns the hashed version of the password
    """
    if salt is None:
        salt = base64.urlsafe_b64encode(hashlib.sha256().digest()).decode('utf-8')
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return f"{salt}${base64.urlsafe_b64encode(hashed).decode('utf-8')}"

async def verify_password(password: str, hashed: str) -> bool:
    """Checks to see if the provided password hash matches the hatched version

    Arguments:
        password (str): The password to check
        hashed (str): The hash to compare with

    Returns:
        matches (bool): Whether the hash and provided password are matching
    
    """
    salt, hash_val = hashed.split('$')
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    new_hash = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return hmac.compare_digest(base64.urlsafe_b64encode(new_hash).decode('utf-8'), hash_val)    
