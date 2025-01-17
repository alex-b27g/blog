from logging import getLogger

from ninja_extra import status

logger = getLogger(__name__)


class ApiException(Exception):
    """
    This is an example of ApiException DTO for checking with tests. You should use your ApiException class
    that will allow to create responses during raising.
    """

    _status_code = 400
    _api_client_message = "Error occurred. Try again."

    def __init__(self, message: str = None, api_client_message: str = None,
                 status_code: int = None):
        # ensure if no data in constructor, use class data

        exception_message = message if message else self._api_client_message
        super().__init__(exception_message)

        self._status_code = status_code if status_code else self._status_code
        self._api_client_message = api_client_message if api_client_message else self._api_client_message

        message_format = f"{self.__class__.__name__} raised: {message}"

        # log error message
        if status.is_client_error(self._status_code):
            logger.warning("Warning" + message_format)
        if status.is_server_error(self._status_code):
            logger.error("Error" + message_format)

    @property
    def api_client_message(self) -> str:
        """
        Gets api_client_message attribute value.

        :return: str
        """
        return self._api_client_message

    @property
    def status_code(self) -> int:
        """
        Gets status code to return in response.

        :return: str
        """
        return self._status_code
