class ApiError(Exception):
    """API error or invalid endpoint URL."""

    def __init__(self, response_code, response_name):
        self.response_code = response_code
        self.response_name = response_name

    def __str__(self):
        return f"""API error or invalid endpoint URL.
        Response code: {self.response_code}, details: {self.response_name}"""


class RequestError(Exception):
    """Request error."""

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return f"An error occured during the request: {self.error}"


class UserListsDontMatch(Exception):
    """Provided responses contain different user lists."""

    def __init__(self, extra_user_name):
        self.extra_user_name = extra_user_name

    def __str__(self):
        return f"""User lists in API responses don't match! 
        Found extra user: {self.extra_user_name}!
        Will stop now."""


class EndpointUrlMissing(Exception):
    """No endpoint URL provided."""

    def __str__(self):
        return f"""No endpoint URL provided."""


class ExpectedKeyNotFound(Exception):
    """Expected key not found."""

    def __init__(self, missing_key):
        self.missing_key = missing_key

    def __str__(self):
        return f"{self.missing_key} Not found"
