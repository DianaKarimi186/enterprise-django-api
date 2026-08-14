from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Return a consistent JSON error structure for REST API responses.
    """

    response = exception_handler(exc, context)

    if response is None:
        return response

    details = response.data

    if isinstance(details, dict) and "detail" in details:
        message = str(details["detail"])
        error_details = None
    else:
        message = "Validation failed."
        error_details = details

    response.data = {
        "error": {
            "status_code": response.status_code,
            "message": message,
            "details": error_details,
        }
    }

    return response