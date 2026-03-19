import time
import requests
from typing import Optional, Dict
from requests.exceptions import RequestException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
)


def _is_retryable(exception):
    retry_status_codes = (500, 502, 429)
    if not isinstance(exception, RequestException):
        return False
    if exception.response.status_code not in retry_status_codes:
        return False
    return True


class HttpClient():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64;'\
            'rv:139.0) Gecko/20100101 Firefox/139.0',
        })

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(_is_retryable),
    )
    def _fetch(self, method: str, url, params=None, json=None, **kwargs):
        resp = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=10,
            **kwargs
        )
        resp.raise_for_status()
        return resp

    def get(self, url, params: Optional[Dict] = None, **kwargs):
        return self._fetch('GET', url, params=params, **kwargs)

    def post(self, url, json: Optional[Dict] = None, **kwargs):
        return self._fetch('POST', url, json=json, **kwargs)

    def close(self):
        self.session.close()
