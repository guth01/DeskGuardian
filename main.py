from core.system_controller import SystemController
from database.db_manager import DBManager
from config.settings import (
    DEFAULT_USER_NAME,
    DEFAULT_USER_AGE,
    DEFAULT_USER_OCCUPATION
)
from utils.logger import Logger


def get_or_create_default_user():
    db = DBManager()

    # Check if user already exists
    db.cursor.execute("SELECT user_id FROM User WHERE name = ?", (DEFAULT_USER_NAME,))
    result = db.cursor.fetchone()

    if result:
        user_id = result[0]
        Logger.info(f"Using existing user: {DEFAULT_USER_NAME} (ID: {user_id})")
    else:
        user_id = db.create_user(
            name=DEFAULT_USER_NAME,
            age=DEFAULT_USER_AGE,
            occupation=DEFAULT_USER_OCCUPATION
        )
        Logger.info(f"Created new user: {DEFAULT_USER_NAME} (ID: {user_id})")

    return user_id


if __name__ == "__main__":

    Logger.info("Starting DeskGuardian Application...")

    user_id = get_or_create_default_user()

    controller = SystemController(user_id)
    controller.start()
