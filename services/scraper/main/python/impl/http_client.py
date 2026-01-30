import time
import requests
from typing import Optional, Dict
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)


class HttpClient():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json;charset=utf-8',
            'X-CSRF-Token': 'ihtroQukudElQnMLFlIYKM7SVByGMOdjB8FydNRjDoafAsCvh1pEhqBqSyCdQJtiCZ6mxjfSDICq_iJOQ1T0Tw',
            'Origin': 'https://www.onlinetours.ru',
            'Connection': 'keep-alive',
            'Referer': 'https://www.onlinetours.ru/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        })

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _fetch(self, method: str, url, params=None, json=None, **kwargs):
        time.sleep(2.1)
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
