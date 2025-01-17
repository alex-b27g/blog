from http.cookies import SimpleCookie

from django.test import AsyncClient

from testing_tools.response_checker import ResponseChecker


class AsyncClientBoB:
    def __init__(self, headers, email: str = None, uid: str = None, password: str = None, organization_id: str = None):
        self.email = email
        self.uid = uid
        self.password = password
        self.organization_id = organization_id
        self.organization_name = None
        self._headers = headers
        self._client = AsyncClient()

    @property
    def headers(self):
        return self._headers

    @property
    def cookies(self):
        return self._client.cookies

    @cookies.setter
    def cookies(self, cookies: dict):
        self._client.cookies = SimpleCookie(cookies)

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    async def get(self, path) -> ResponseChecker:
        response = await self._client.get(path, headers=self._headers)
        response_checker = ResponseChecker(response)
        return response_checker

    async def post(self, path, data, content_type='application/json') -> ResponseChecker:
        response = await self._client.post(path, data, content_type=content_type, headers=self._headers)
        response_checker = ResponseChecker(response)
        return response_checker

    async def patch(self, path, data, content_type) -> ResponseChecker:
        response = await self._client.patch(path, data, content_type=content_type, headers=self._headers)
        response_checker = ResponseChecker(response)
        return response_checker

    async def delete(self, path) -> ResponseChecker:
        response = await self._client.delete(path, headers=self._headers)
        response_checker = ResponseChecker(response)
        return response_checker
