import bcrypt
import random
import string


def hash_password(password: str) -> bytes:
    pw = bytes(password, 'utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


def check_password(password: str, password_in_db: bytes) -> bool:
    password_bytes = bytes(password, 'utf-8')
    return bcrypt.checkpw(password_bytes, password_in_db)


def generate_alphanum_random_string(length: int = 25) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=length))
