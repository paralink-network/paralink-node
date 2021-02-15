import logging
import typing

import stdiomask

logger = logging.getLogger(__name__)


def user_prompt() -> typing.Tuple[str, str]:
    """Prompts user for username and password.

    Returns:
        (str, str): (username, password)
    """
    username = input("Please enter your username: ")
    password = stdiomask.getpass("Enter your password: ")

    while True:
        confirm_password = stdiomask.getpass("Reenter your password: ")

        if password == confirm_password:
            break
        else:
            print("Passwords do not match. Please try again.")

    return username, password
