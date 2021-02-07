from jsonschema import Draft7Validator
from sanic.exceptions import InvalidUsage


def validate_request(request: dict, schema: dict) -> None:
    """Validate api request.

    Args:
        request: request dictionary.
        schema: schema to validate against.

    Returns:
        None if validation is successful.

    Raises:
          InvalidUsage: if request request does not adhere to the schema.
    """
    errors = [error for error in Draft7Validator(schema).iter_errors(request)]
    if errors:
        message = "\n".join(
            [
                (".".join(error.path) + " - " if error.path else "") + error.message
                for error in errors
            ]
        )
        raise InvalidUsage(f"Request does not adhere to schema \n{message}")
