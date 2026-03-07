import hashlib
import os
from database.db_manager import DBManager
from utils.logger import Logger


class AuthService:
    """
    Authentication service for DeskGuardian.
    Handles user registration and login with hashed passwords.
    """

    def __init__(self):
        self.db = DBManager()

    # ======================================
    # PASSWORD HASHING
    # ======================================

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password with a random salt using SHA-256."""
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return salt.hex() + ":" + pwd_hash.hex()

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        """Verify a password against a stored salt:hash string."""
        try:
            salt_hex, hash_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
            return pwd_hash.hex() == hash_hex
        except Exception:
            return False

    # ======================================
    # SIGNUP
    # ======================================

    def signup(self, username: str, password: str, age: int, occupation: str = ""):
        """
        Register a new user.

        Returns:
            (user_id, None) on success
            (None, error_message) on failure
        """
        if not username or not password:
            return None, "Username and password are required."

        if len(password) < 4:
            return None, "Password must be at least 4 characters."

        if age < 1 or age > 150:
            return None, "Please enter a valid age."

        # Check if username already taken
        existing = self.db.get_user_by_name(username)
        if existing:
            return None, "Username already exists. Please choose another."

        try:
            password_hash = self._hash_password(password)
            user_id = self.db.create_user(
                name=username,
                password_hash=password_hash,
                age=age,
                occupation=occupation,
            )
            Logger.info(f"New user registered: {username} (ID: {user_id})")
            return user_id, None
        except Exception as e:
            Logger.error(f"Signup error: {e}")
            return None, f"Registration failed: {e}"

    # ======================================
    # LOGIN
    # ======================================

    def login(self, username: str, password: str):
        """
        Authenticate a user.

        Returns:
            (user_id, None) on success
            (None, error_message) on failure
        """
        if not username or not password:
            return None, "Username and password are required."

        user_row = self.db.get_user_by_name(username)
        if user_row is None:
            return None, "User not found. Please sign up first."

        user_id, name, stored_hash, age, occupation = user_row

        if not self._verify_password(password, stored_hash):
            return None, "Incorrect password."

        Logger.info(f"User logged in: {username} (ID: {user_id})")
        return user_id, None
