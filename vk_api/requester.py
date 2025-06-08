import json
from urllib.request import urlopen

_API_URL = 'https://api.vk.com/method/{}?{}&v={}&access_token={}'
_VERSION = '5.81'


class VkApiRequester:
    def __init__(self, token: str):
        self._token: str = token

    def make_request(self, method: str, fields: str) -> object:
        request = _API_URL.format(method, fields, _VERSION, self._token)
        with urlopen(request) as url:
            return json.loads(url.read())