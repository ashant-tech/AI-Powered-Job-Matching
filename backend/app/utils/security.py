from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    """
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal attacks.
    """
    import os
    # Remove path components
    filename = os.path.basename(filename)
    # Remove potentially dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in '._-')
    return filename

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """
    Validate file type against allowed types.
    """
    file_extension = filename.split('.')[-1].lower()
    return file_extension in allowed_types
