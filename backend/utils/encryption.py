from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64
import os
from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from typing import Tuple, Optional
import gnupg
from ..config import ENCRYPTION_KEY

class Encryption:
    def __init__(self):
        # Initialize Fernet for symmetric encryption
        self.fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)
        
        # Initialize GPG for PGP operations
        self.gpg = gnupg.GPG(gnupghome=os.path.join(os.getcwd(), 'gpghome'))
        
        # Ensure GPG home directory exists
        os.makedirs(self.gpg.gnupghome, exist_ok=True)

    def encrypt_file(self, file_data: bytes) -> Tuple[bytes, str]:
        """
        Encrypts file data using Fernet (symmetric encryption)
        Returns: (encrypted_data, file_key)
        """
        try:
            # Generate a unique key for this file
            file_key = Fernet.generate_key()
            f = Fernet(file_key)
            
            # Encrypt the file data
            encrypted_data = f.encrypt(file_data)
            
            # Return both the encrypted data and the key needed to decrypt it
            return encrypted_data, base64.b64encode(file_key).decode()
        except Exception as e:
            raise Exception(f"File encryption failed: {str(e)}")

    def decrypt_file(self, encrypted_data: bytes, file_key: str) -> bytes:
        """
        Decrypts file data using the provided key
        """
        try:
            f = Fernet(base64.b64decode(file_key))
            return f.decrypt(encrypted_data)
        except Exception as e:
            raise Exception(f"File decryption failed: {str(e)}")

    def encrypt_message(self, message: str, recipient_pgp_key: str) -> str:
        """
        Encrypts a message using recipient's PGP public key
        """
        try:
            # Import recipient's public key
            import_result = self.gpg.import_keys(recipient_pgp_key)
            if not import_result.fingerprints:
                raise ValueError("Invalid PGP key")
            
            # Encrypt the message
            encrypted_data = self.gpg.encrypt(
                message,
                import_result.fingerprints[0],
                always_trust=True
            )
            
            if not encrypted_data.ok:
                raise Exception(f"Encryption failed: {encrypted_data.status}")
            
            return str(encrypted_data)
        except Exception as e:
            raise Exception(f"Message encryption failed: {str(e)}")

    def verify_pgp_key(self, pgp_key: str) -> bool:
        """
        Verifies if a PGP key is valid
        """
        try:
            import_result = self.gpg.import_keys(pgp_key)
            return bool(import_result.fingerprints)
        except Exception:
            return False

    def generate_file_key(self) -> str:
        """
        Generates a new encryption key for file encryption
        """
        return base64.b64encode(Fernet.generate_key()).decode()

# Create a global instance
encryption = Encryption()

# Utility functions for easy access
def encrypt_file_data(file_data: bytes) -> Tuple[bytes, str]:
    return encryption.encrypt_file(file_data)

def decryptNext, let's create the encryption utility file to handle AES-256 encryption and decryption of files:

<create_file>
<path>backend/utils/encryption.py</path>
<content>from cryptography.fernet import Fernet
from backend.config import ENCRYPTION_KEY

# Initialize Fernet cipher
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypt data using Fernet symmetric encryption.
    """
    return cipher.encrypt(data)

def decrypt_data(token: bytes) -> bytes:
    """
    Decrypt data using Fernet symmetric encryption.
    """
    return cipher.decrypt(token)
