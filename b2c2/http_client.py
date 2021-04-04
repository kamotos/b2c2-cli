from dataclasses import dataclass
from urllib.parse import urljoin

import funcy
import requests
import typing
from requests.exceptions import ConnectTimeout, ConnectionError, HTTPError, Timeout


def is_timeout_or_server_error(error: typing.Union[HTTPError, ConnectTimeout]) -> bool:
    """
    :return: True if `error` is a timeout or connection error or if it's a server error
    """
    is_timeout = isinstance(error, (ConnectTimeout, ConnectionError, Timeout))
    is_server_error = isinstance(error, HTTPError) and error.response.status_code >= 500
    return is_timeout or is_server_error


@dataclass
class B2C2Client:
    url: str
    token: str

    def request_for_quote(self, **kwargs):
        return self.http_request('POST', 'request_for_quote/', json=kwargs)

    def post_order(self, **kwargs):
        return self.http_request('POST', 'order/', json=kwargs)

    @funcy.retry(
        5,
        errors=(HTTPError, ConnectTimeout, Timeout, ConnectTimeout),
        filter_errors=is_timeout_or_server_error,
    )
    def http_request(
            self,
            method: str,
            endpoint: str,
            params: dict = None,
            headers: dict = None,
            json=None,
    ):
        url = urljoin(self.url, endpoint)
        headers = headers or {}
        headers['Authorization'] = f"Token {self.token}"
        response = requests.request(method, url, params=params, headers=headers, json=json)
        response.raise_for_status()
        return response.json()

    def instruments(self):
        return self.http_request('GET', 'instruments/')

    def balance(self):
        return self.http_request('GET', 'balance/')

    def account_info(self):
        return self.http_request('GET', 'account_info/')

