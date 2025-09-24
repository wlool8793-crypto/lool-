"""
Data Encryption and Protection System

Provides comprehensive encryption capabilities for sensitive data:
- Data-at-rest encryption with AES-256-GCM
- Data-in-transit encryption management
- Key management and rotation
- Field-level encryption for sensitive fields
- Configuration and secrets encryption
- Secure data handling practices
"""

import os
import json
import base64
import secrets
import hashlib
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, InvalidTag
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EncryptionConfig:
    """Configuration for encryption operations"""
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    enable_key_derivation: bool = True
    secure_random: bool = True
    memory_cost: int = 65536  # For Scrypt KDF
    parallelism: int = 4
    iterations: int = 100000


@dataclass
class EncryptionKey:
    """Represents an encryption key with metadata"""
    key_id: str
    key_material: bytes
    algorithm: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    key_type: str = "encryption"  # encryption, signing, wrapping
    key_size: int = 256
    key_purpose: str = "general"


class EncryptionManager:
    """Manages encryption operations and key lifecycle"""

    def __init__(self, config: EncryptionConfig):
        self.config = config
        self.keys: Dict[str, EncryptionKey] = {}
        self.field_encryption_rules: Dict[str, Dict[str, Any]] = {}
        self.initialize_system()

    def initialize_system(self):
        """Initialize encryption system with master key"""
        logger.info("Initializing encryption system")

        # Load or create master encryption key
        master_key = self._load_or_create_master_key()
        self.keys["master"] = master_key

        # Initialize field encryption rules
        self._initialize_field_rules()

        logger.info("Encryption system initialized successfully")

    def _load_or_create_master_key(self) -> EncryptionKey:
        """Load existing master key or create new one"""
        master_key_path = os.getenv("MASTER_KEY_PATH", "data/master_key.enc")

        if os.path.exists(master_key_path):
            try:
                with open(master_key_path, "rb") as f:
                    key_data = f.read()

                # Decrypt master key (requires environment key)
                env_key = os.getenv("MASTER_ENCRYPTION_KEY")
                if not env_key:
                    raise ValueError("MASTER_ENCRYPTION_KEY environment variable required")

                key_material = self._decrypt_key(key_data, env_key)

                return EncryptionKey(
                    key_id="master",
                    key_material=key_material,
                    algorithm=self.config.algorithm,
                    key_type="encryption",
                    key_purpose="master"
                )
            except Exception as e:
                logger.error(f"Failed to load master key: {e}")
                raise

        # Generate new master key
        return self._generate_encryption_key("master", "master")

    def _generate_encryption_key(self, key_id: str, key_purpose: str) -> EncryptionKey:
        """Generate a new encryption key"""
        if self.config.algorithm == "AES-256-GCM":
            key_material = secrets.token_bytes(32)  # 256 bits
        else:
            key_material = Fernet.generate_key()

        expiry_date = datetime.now() + timedelta(days=self.config.key_rotation_days)

        key = EncryptionKey(
            key_id=key_id,
            key_material=key_material,
            algorithm=self.config.algorithm,
            expires_at=expiry_date,
            key_type="encryption",
            key_purpose=key_purpose,
            key_size=len(key_material) * 8
        )

        self.keys[key_id] = key

        # Save master key
        if key_id == "master":
            self._save_master_key(key)

        logger.info(f"Generated new encryption key: {key_id}")
        return key

    def _save_master_key(self, key: EncryptionKey):
        """Save master key encrypted with environment key"""
        env_key = os.getenv("MASTER_ENCRYPTION_KEY")
        if not env_key:
            raise ValueError("MASTER_ENCRYPTION_KEY environment variable required")

        encrypted_key = self._encrypt_key(key.key_material, env_key)

        os.makedirs("data", exist_ok=True)
        master_key_path = os.getenv("MASTER_KEY_PATH", "data/master_key.enc")

        with open(master_key_path, "wb") as f:
            f.write(encrypted_key)

        # Set secure permissions
        os.chmod(master_key_path, 0o600)

        logger.info("Master key saved securely")

    def _encrypt_key(self, key_material: bytes, password: str) -> bytes:
        """Encrypt key material with password using PBKDF2"""
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = kdf.derive(password.encode())
        cipher = Cipher(algorithms.AES(key), modes.GCM(secrets.token_bytes(12)))
        encryptor = cipher.encryptor()

        encrypted = encryptor.update(key_material) + encryptor.finalize()
        return salt + encryptor.tag + encrypted

    def _decrypt_key(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt key material with password"""
        salt = encrypted_data[:16]
        tag = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = kdf.derive(password.encode())
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag))
        decryptor = cipher.decryptor()

        try:
            return decryptor.update(ciphertext) + decryptor.finalize()
        except InvalidTag:
            raise ValueError("Failed to decrypt key - invalid password or corrupted data")

    def _initialize_field_rules(self):
        """Initialize field-level encryption rules"""
        self.field_encryption_rules = {
            # User data
            "users": {
                "encrypted_fields": ["email", "phone", "address", "ssn", "date_of_birth"],
                "hash_fields": ["password"],
                "token_fields": ["api_key", "auth_token"],
                "partial_fields": {
                    "email": {"show": "first_part", "hide_chars": 3},
                    "phone": {"show": "last_4", "format": "***-***-####"}
                }
            },
            # Payment data
            "payments": {
                "encrypted_fields": ["card_number", "bank_account", "routing_number", "cvv"],
                "token_fields": ["payment_token", "transaction_id"],
                "redact_fields": ["card_number", "cvv"],
                "mask_fields": {
                    "card_number": "************####",
                    "cvv": "***"
                }
            },
            # Personal identifiable information
            "pii": {
                "encrypted_fields": ["full_name", "id_number", "license_number", "passport_number"],
                "hash_fields": ["identifier"],
                "access_control": "strict"
            },
            # Configuration data
            "config": {
                "encrypted_fields": ["api_secret", "webhook_secret", "database_password"],
                "hash_fields": ["webhook_url"],
                "key_rotation": True
            }
        }

        logger.info("Field encryption rules initialized")

    def encrypt_data(self, data: Union[str, bytes, Dict], key_id: str = "master") -> Dict[str, Any]:
        """Encrypt data with specified key"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        key = self.keys[key_id]

        if not key.is_active:
            raise ValueError(f"Key {key_id} is not active")

        if datetime.now() > (key.expires_at or datetime.max):
            raise ValueError(f"Key {key_id} has expired")

        # Convert to bytes if needed
        if isinstance(data, str):
            plaintext = data.encode('utf-8')
        elif isinstance(data, dict):
            plaintext = json.dumps(data).encode('utf-8')
        else:
            plaintext = data

        # Generate IV for AES-GCM
        iv = secrets.token_bytes(12)

        if key.algorithm == "AES-256-GCM":
            cipher = Cipher(algorithms.AES(key.key_material), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()

            return {
                "key_id": key_id,
                "algorithm": key.algorithm,
                "iv": base64.b64encode(iv).decode('utf-8'),
                "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                "tag": base64.b64encode(encryptor.tag).decode('utf-8'),
                "encrypted_at": datetime.now().isoformat()
            }
        else:
            # Use Fernet for symmetric encryption
            fernet = Fernet(base64.b64encode(key.key_material))
            ciphertext = fernet.encrypt(plaintext)

            return {
                "key_id": key_id,
                "algorithm": "Fernet",
                "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                "encrypted_at": datetime.now().isoformat()
            }

    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> Union[str, bytes, Dict]:
        """Decrypt data"""
        key_id = encrypted_data.get("key_id", "master")
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        key = self.keys[key_id]

        if key.algorithm == "AES-256-GCM":
            iv = base64.b64decode(encrypted_data["iv"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            tag = base64.b64decode(encrypted_data["tag"])

            cipher = Cipher(algorithms.AES(key.key_material), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()

            try:
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            except InvalidTag:
                raise ValueError("Decryption failed - invalid tag or corrupted data")

            # Try to parse as JSON, otherwise return as string
            try:
                return json.loads(plaintext.decode('utf-8'))
            except:
                return plaintext.decode('utf-8')

        else:
            # Fernet decryption
            fernet = Fernet(base64.b64encode(key.key_material))
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            plaintext = fernet.decrypt(ciphertext)

            try:
                return json.loads(plaintext.decode('utf-8'))
            except:
                return plaintext.decode('utf-8')

    def encrypt_field(self, field_name: str, value: Any, table_name: str = "default") -> str:
        """Encrypt a specific field based on rules"""
        rules = self.field_encryption_rules.get(table_name, {})

        if field_name in rules.get("hash_fields", []):
            return self._hash_sensitive_data(value)
        elif field_name in rules.get("token_fields", []):
            return self._generate_token_for_field(value, field_name)
        elif field_name in rules.get("encrypted_fields", []):
            encrypted = self.encrypt_data(str(value))
            return json.dumps(encrypted)
        else:
            return str(value)

    def decrypt_field(self, field_name: str, encrypted_value: str, table_name: str = "default") -> Any:
        """Decrypt a specific field"""
        rules = self.field_encryption_rules.get(table_name, {})

        if field_name in rules.get("encrypted_fields", []):
            try:
                encrypted_data = json.loads(encrypted_value)
                return self.decrypt_data(encrypted_data)
            except:
                return encrypted_value
        else:
            return encrypted_value

    def _hash_sensitive_data(self, data: Any) -> str:
        """Hash sensitive data using SHA-256 with salt"""
        salt = secrets.token_bytes(16)
        data_str = str(data).encode('utf-8')

        kdf = Scrypt(
            salt=salt,
            length=64,
            n=self.config.memory_cost,
            r=8,  # Block size
            p=self.config.parallelism,
            backend=default_backend()
        )

        hashed = kdf.derive(data_str)
        return base64.b64encode(salt + hashed).decode('utf-8')

    def _generate_token_for_field(self, data: Any, field_name: str) -> str:
        """Generate a secure token for field"""
        # Use HMAC-SHA256 for token generation
        secret = os.getenv("TOKEN_SECRET", "default_secret")
        data_str = str(data).encode('utf-8')

        hmac = hashlib.pbkdf2_hmac('sha256', data_str, secret.encode(), 100000)
        return base64.b64encode(hmac).decode('utf-8')

    def mask_sensitive_data(self, field_name: str, value: Any, table_name: str = "default") -> str:
        """Apply masking rules to sensitive data"""
        rules = self.field_encryption_rules.get(table_name, {})

        if field_name in rules.get("redact_fields", []):
            return "[REDACTED]"

        masking_rules = rules.get("mask_fields", {})
        if field_name in masking_rules:
            mask_pattern = masking_rules[field_name]

            if field_name == "card_number":
                # Show last 4 digits
                return mask_pattern.replace("####", str(value)[-4:])
            elif field_name == "cvv":
                return "***"
            else:
                return mask_pattern

        partial_rules = rules.get("partial_fields", {})
        if field_name in partial_rules:
            rule = partial_rules[field_name]
            show_type = rule.get("show", "first_part")
            hide_chars = rule.get("hide_chars", 0)

            if show_type == "first_part":
                if len(str(value)) > hide_chars:
                    return str(value)[:-hide_chars] + "*" * hide_chars
            elif show_type == "last_4":
                if len(str(value)) >= 4:
                    return "***" + str(value)[-4:]

        return str(value)

    def rotate_keys(self):
        """Rotate encryption keys"""
        logger.info("Starting key rotation")

        expired_keys = [
            key for key in self.keys.values()
            if key.expires_at and datetime.now() > key.expires_at
        ]

        for old_key in expired_keys:
            logger.info(f"Rotating key: {old_key.key_id}")

            # Generate new key
            new_key = self._generate_encryption_key(
                f"{old_key.key_id}_new",
                old_key.key_purpose
            )

            # Deactivate old key
            old_key.is_active = False

            logger.info(f"Key {old_key.key_id} rotated successfully")

        logger.info("Key rotation completed")

    def generate_key_pair(self, key_id: str) -> tuple[EncryptionKey, EncryptionKey]:
        """Generate RSA key pair for asymmetric encryption"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        private_encryption_key = EncryptionKey(
            key_id=f"{key_id}_private",
            key_material=private_pem,
            algorithm="RSA-2048",
            key_type="private",
            key_purpose="signing"
        )

        public_encryption_key = EncryptionKey(
            key_id=f"{key_id}_public",
            key_material=public_pem,
            algorithm="RSA-2048",
            key_type="public",
            key_purpose="verification"
        )

        self.keys[private_encryption_key.key_id] = private_encryption_key
        self.keys[public_encryption_key.key_id] = public_encryption_key

        return private_encryption_key, public_encryption_key

    def sign_data(self, data: Union[str, bytes], private_key_id: str) -> str:
        """Sign data with private key"""
        if private_key_id not in self.keys:
            raise ValueError(f"Private key {private_key_id} not found")

        key = self.keys[private_key_id]

        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        private_key = serialization.load_pem_private_key(
            key.key_material,
            password=None,
            backend=default_backend()
        )

        signature = private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, data: Union[str, bytes], signature: str, public_key_id: str) -> bool:
        """Verify signature with public key"""
        if public_key_id not in self.keys:
            raise ValueError(f"Public key {public_key_id} not found")

        key = self.keys[public_key_id]

        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        signature_bytes = base64.b64decode(signature)

        public_key = serialization.load_pem_public_key(
            key.key_material,
            backend=default_backend()
        )

        try:
            public_key.verify(
                signature_bytes,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def get_encryption_status(self) -> Dict[str, Any]:
        """Get encryption system status"""
        active_keys = [k for k in self.keys.values() if k.is_active]
        expired_keys = [k for k in self.keys.values() if not k.is_active]

        return {
            "status": "active",
            "total_keys": len(self.keys),
            "active_keys": len(active_keys),
            "expired_keys": len(expired_keys),
            "field_rules_count": len(self.field_encryption_rules),
            "default_algorithm": self.config.algorithm,
            "key_rotation_days": self.config.key_rotation_days,
            "master_key_age": (
                datetime.now() - self.keys["master"].created_at
            ).days if "master" in self.keys else 0
        }

    def secure_delete(self, data: Union[str, bytes], passes: int = 3):
        """Securely delete sensitive data"""
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        # Multiple overwrite passes
        for i in range(passes):
            # Random pattern
            random_data = secrets.token_bytes(len(data_bytes))
            data_bytes = random_data

            # Zero pattern
            zero_data = b'\x00' * len(data_bytes)
            data_bytes = zero_data

            # One pattern
            one_data = b'\xFF' * len(data_bytes)
            data_bytes = one_data

        logger.info("Data securely deleted")

    def encrypt_environment_variables(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Encrypt environment variables for secure storage"""
        encrypted_vars = {}

        for key, value in env_vars.items():
            if any(sensitive in key.lower() for sensitive in ['secret', 'key', 'password', 'token']):
                encrypted_value = self.encrypt_data(value)
                encrypted_vars[key] = json.dumps(encrypted_value)
            else:
                encrypted_vars[key] = value

        return encrypted_vars

    def decrypt_environment_variables(self, encrypted_vars: Dict[str, str]) -> Dict[str, str]:
        """Decrypt environment variables"""
        decrypted_vars = {}

        for key, value in encrypted_vars.items():
            try:
                # Try to parse as encrypted data
                encrypted_data = json.loads(value)
                if isinstance(encrypted_data, dict) and "ciphertext" in encrypted_data:
                    decrypted_vars[key] = self.decrypt_data(encrypted_data)
                else:
                    decrypted_vars[key] = value
            except:
                decrypted_vars[key] = value

        return decrypted_vars