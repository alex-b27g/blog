from httpx import Response
from ninja_extra import status

from your_app_utils.api_exception import ApiException
from your_app_utils.pagination import PaginationDTO


class ResponseChecker:
    """
    Class responsible for response checking during end-to-end testing.
    """

    def __init__(self, resposne: Response):
        """
        Initialize the ResponseChecker with a response object.
        Automatically processes the response to extract status and JSON content.
        """
        self._response = resposne
        self._status = None
        self._json = None
        self._process_response()

    def _process_response(self):
        """
        Extracts JSON data and status code from the response object.
        If the response has no content, sets JSON to an empty dictionary.
        """
        self._json = self._response.json() if self._response.content else {}
        self._status = self._response.status_code

    def key_value(self, key: str) -> dict | object | str:
        """
        Retrieve a specific key's value from the response JSON.
        Asserts if the key is not found in the JSON data.
        :param key: Key to search for in the JSON data.
        :return: Value associated with the key.
        """
        value = self._json.get(key, None)
        assert value, f"Key {key} not found in response data."
        return value

    def has_cookies(self, key: str) -> str:
        """
        Check if a specific cookie key exists in the response cookies.
        Asserts if the key is not present.
        :param key: Cookie key to check.
        :return: Value of the cookie.
        """
        cookies = self._response.cookies
        assert key in cookies, f"Key {key} is not in cookies."
        return cookies[key].value

    def paginated(self, min_number_of_records: int = 0):
        """
        Validate and retrieve pagination data and results from the response JSON.
        Asserts if results or pagination data are missing or insufficient.
        :param min_number_of_records: Minimum required number of records.
        :return: Tuple containing results and pagination data.
        """
        results = self._json.get("results", None)
        pagination_data = self._json.get("pagination", None)
        results_number = len(results)
        assert results_number > 0, f"Results number is {results_number}, " \
                                   f"but should be at least {min_number_of_records}"
        assert results is not None, "No results data"
        assert pagination_data is not None, "No pagination data"
        pagination = PaginationDTO(**pagination_data)
        return results, pagination

    def check_exception(self, api_exception: ApiException):
        """
        Verify that the response matches the expected API exception.
        Asserts if the status code or error message does not match.
        :param api_exception: Expected API exception to validate against.
        """
        exception_status_code = getattr(api_exception, '_status_code')
        assert self._response.status_code == exception_status_code, f"Status is: {self._status} " \
                                                                    f"but should be: {exception_status_code}"
        error_message = getattr(api_exception, '_api_client_message')
        message = self.key_value("message")
        assert error_message == message, f"Message to client is: {message}" \
                                         f"but should be: {error_message}"

    def validate_status(self, code: status):
        """
        Validate that the response status matches the expected code.
        Asserts if the status does not match.
        :param code: Expected status code.
        """
        assert self._status == code, f"Status is {self._status} but should be {code}"

    def is_informational(self):
        """
        Check if the response status indicates an informational response.
        Asserts if the status is not informational.
        """
        assert status.is_informational(self._status), f"Status is {self._status}"

    def is_success(self):
        """
        Check if the response status indicates a successful response.
        Asserts if the status is not successful.
        """
        assert status.is_success(self._status), f"Status is {self._status}"

    def is_redirect(self):
        """
        Check if the response status indicates a redirect.
        Asserts if the status is not a redirect.
        """
        assert status.is_redirect(self._status), f"Status is {self._status}"

    def is_client_error(self):
        """
        Check if the response status indicates a client error.
        Asserts if the status is not a client error.
        """
        assert status.is_client_error(self._status), f"Status is {self._status}"

    def is_server_error(self):
        """
        Check if the response status indicates a server error.
        Asserts if the status is not a server error.
        """
        assert status.is_server_error(self._status), f"Status is {self._status}"
