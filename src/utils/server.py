from jsonschema import Draft7Validator
from sanic.exceptions import InvalidUsage


def validate_request(request: dict, schema: dict) -> None:
    errors = Draft7Validator(schema).iter_errors(request)
    if errors:
        message = "\n".join(
            [
                (".".join(error.path) + " - " if error.path else "") + error.message
                for error in errors
            ]
        )
        raise InvalidUsage(f"Request does not adhere to schema \n{message}")
