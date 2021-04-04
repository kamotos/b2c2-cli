import pytest
from requests import Response
from requests.exceptions import ConnectionError, ConnectTimeout, Timeout, HTTPError
import responses

from b2c2.http_client import is_timeout_or_server_error, B2C2Client

client_error_response = Response()
client_error_response.status_code = 400
server_error_response = Response()
server_error_response.status_code = 500
client = B2C2Client(url="https://foo.bar", token="fake_token")


@pytest.mark.parametrize("exception,expected", (
        (ConnectionError(), True),
        (Timeout(), True),
        (ConnectTimeout(), True),
        (HTTPError(response=server_error_response), True),
        (HTTPError(response=client_error_response), False),
))
def test_is_timeout_or_server_error(exception, expected):
    assert is_timeout_or_server_error(exception) == expected


@responses.activate
def test_retry():
    """We expected that there should be 5 retries"""

    responses.add(responses.GET, 'https://foo.bar/balance/', status=500)
    responses.add(responses.GET, 'https://foo.bar/balance/', status=500)
    responses.add(responses.GET, 'https://foo.bar/balance/', status=500)
    responses.add(responses.GET, 'https://foo.bar/balance/', status=500)
    responses.add(responses.GET, 'https://foo.bar/balance/', status=200, json={})

    client.balance()


@responses.activate
def test_http_request():
    json_body = {"my": ["json", "body"]}
    responses.add(
        responses.POST,
        'https://foo.bar/my-endpoint', status=200,
        match=[responses.json_params_matcher(json_body)],
        json={"my": "response body"},
    )

    client.http_request('POST', 'my-endpoint', params={'param-key': 'val'}, json=json_body)
    assert responses.calls[0].request.headers["Authorization"] == "Token fake_token"
