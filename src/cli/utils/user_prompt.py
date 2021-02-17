import logging
import typing

import stdiomask

logger = logging.getLogger(__name__)


def user_prompt() -> typing.Tuple[str, str]:
    """Prompts user for username and password.

    Returns:
        (str, str): (username, password)
    """

    # Username
    while True:
        username = input("Please enter your username: ")
        if len(username) > 1:
            break
        else:
            print("Username is too short, try again.")

    # Password
    while True:
        password = stdiomask.getpass("Enter your password (at least 8 characters): ")

        if len(password) > 7:
            break
        else:
            print("Password is too short (at least 8 characters), try again.")

    # Confirm password
    while True:
        confirm_password = stdiomask.getpass("Reenter your password: ")

        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    return username, password
