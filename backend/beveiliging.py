import hashlib
from cryptography.fernet import Fernet

def hash_pincode(pincode: str) -> str:
    return hashlib.sha256(pincode.encode()).hexdigest()

def genereer_sleutel():
    return Fernet.generate_key()

def versleutel_data(data: str, sleutel: bytes) -> str:
    f = Fernet(sleutel)
    return f.encrypt(data.encode()).decode()

def ontsleutel_data(token: str, sleutel: bytes) -> str:
    f = Fernet(sleutel)
    return f.decrypt(token.encode()).decode()
