"""
Hash Generator for Content Integrity Verification
Generates 16-character (64-bit) hash for legal document filenames
"""

import hashlib
from typing import Optional


class HashGenerator:
    """
    Generate content hashes for legal documents.
    Uses SHA-256 and returns first 16 characters for filename use.
    """

    HASH_LENGTH = 16  # 64 bits = 16 hex characters

    @staticmethod
    def generate_hash(content: str) -> str:
        """
        Generate 16-character hash from text content.

        Args:
            content: Text content to hash

        Returns:
            16-character uppercase hex string

        Example:
            >>> HashGenerator.generate_hash("The Penal Code, 1860")
            'A3F4B2C1D5E6F7G8'
        """
        if not content:
            return "0" * HashGenerator.HASH_LENGTH

        # Use SHA-256 for security
        sha256_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Return first 16 characters (64 bits) in uppercase
        return sha256_hash[:HashGenerator.HASH_LENGTH].upper()

    @staticmethod
    def generate_file_hash(file_path: str) -> Optional[str]:
        """
        Generate 16-character hash from file content.

        Args:
            file_path: Path to file

        Returns:
            16-character uppercase hex string, or None if file not found
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()[:HashGenerator.HASH_LENGTH].upper()
        except (FileNotFoundError, IOError):
            return None

    @staticmethod
    def generate_combined_hash(text_content: str, pdf_path: Optional[str] = None) -> str:
        """
        Generate combined hash from text and PDF content.

        Args:
            text_content: Extracted text content
            pdf_path: Optional path to PDF file

        Returns:
            16-character uppercase hex string
        """
        combined = text_content or ""

        if pdf_path:
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()
                combined += pdf_content.hex()
            except (FileNotFoundError, IOError):
                pass

        return HashGenerator.generate_hash(combined)

    @staticmethod
    def validate_hash(hash_string: str) -> bool:
        """
        Validate hash format (16 hex characters).

        Args:
            hash_string: Hash to validate

        Returns:
            True if valid format
        """
        if not hash_string or len(hash_string) != HashGenerator.HASH_LENGTH:
            return False

        try:
            int(hash_string, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> bool:
        """
        Compare two hashes (case-insensitive).

        Args:
            hash1: First hash
            hash2: Second hash

        Returns:
            True if hashes match
        """
        if not hash1 or not hash2:
            return False
        return hash1.upper() == hash2.upper()


if __name__ == "__main__":
    # Test hash generator
    print("Testing Hash Generator...")

    # Test text hash
    text = "The Penal Code, 1860"
    hash1 = HashGenerator.generate_hash(text)
    print(f"Text: '{text}'")
    print(f"Hash: {hash1}")
    print(f"Length: {len(hash1)}")
    print(f"Valid: {HashGenerator.validate_hash(hash1)}")

    # Test empty content
    empty_hash = HashGenerator.generate_hash("")
    print(f"\nEmpty content hash: {empty_hash}")

    # Test same content produces same hash
    hash2 = HashGenerator.generate_hash(text)
    print(f"\nSame content match: {HashGenerator.compare_hashes(hash1, hash2)}")

    # Test different content
    hash3 = HashGenerator.generate_hash("Different text")
    print(f"Different content match: {HashGenerator.compare_hashes(hash1, hash3)}")
