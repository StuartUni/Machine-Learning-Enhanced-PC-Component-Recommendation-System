"""
Created by: Stuart Smith
Student ID: S2336002
Date Created: 26/03/2025
Description:
This module handles password hashing and verification using bcrypt. It ensures that user passwords
are securely stored and compared when authenticating users.
"""

import bcrypt

class Hasher:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes a plaintext password using bcrypt.
        
        :param password: The plaintext password to be hashed.
        :return: The hashed password as a string.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")  

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password against its stored hash.
        
        :param plain_password: The user-provided password.
        :param hashed_password: The hashed password from the database.
        :return: True if passwords match, False otherwise.
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

#  Testing Hashing Functionality
if __name__ == "__main__":
    test_password = "securepassword123"
    hashed = Hasher.hash_password(test_password)
    print(f" Hashed Password: {hashed}")

    is_valid = Hasher.verify_password("securepassword123", hashed)
    print(f" Password Match: {is_valid}")

    is_invalid = Hasher.verify_password("wrongpassword", hashed)
    print(f" Wrong Password Match: {is_invalid}")