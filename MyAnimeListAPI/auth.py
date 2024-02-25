import secrets
import time
from base64 import b64encode
from json import loads
from urllib.parse import quote_plus

import requests as rq

from . import enums


class BaseAuth:
    auth_url = "https://myanimelist.net"
    auth_ver = "v1"
    auth_code_path = "/oauth2/authorize"
    auth_token_path = "/oauth2/token"

    def __init__(
            self,
            client_id: str,
            token_type: enums.TokenType
    ):
        self.client_id = str(client_id)
        self._token_type = token_type
        self_access_token = ""

    @staticmethod
    def _make_url(base_url: str, url_path: str | list[str] = None, url_params: dict = None) -> str:
        new_url = str(base_url)
        if type(url_path) is str:
            new_url += str(url_path)
        elif type(url_path) == list:
            for i in url_path:
                if not i.startswith("/"):
                    new_url += "/"
                new_url += i
        if url_params is None:
            return new_url

        new_url += "?"
        iteration = 0
        for i in url_params:
            new_url += i + "=" + quote_plus(url_params[i])
            if not iteration == url_params.__len__() - 1:
                new_url += "&"
            iteration += 1
        return new_url

    @staticmethod
    def _get_expiry_time_unix(expire_in: int):
        # minus 1min so we can be sure not to get an expired token error
        # int() because we don't need a millisecond precision, but a second precision
        unix_now = int(time.time()) - 60
        return unix_now + expire_in

    @property
    def auth_header(self):
        raise NotImplementedError("You forgot to implement the auth_header getter.")


class MainAuth(BaseAuth):
    def __init__(self,
                 client_id: str,
                 client_secret: str = "",
                 callback_url: str = "http://localhost"
                 ):

        super().__init__(client_id=client_id, token_type=enums.TokenType.BEARER)
        self.client_secret = client_secret
        self.client_basic = str(b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")))
        self.callback_url = callback_url
        self._access_token = ""
        self.refresh_token = ""
        self._token_expiry_unix = ""

    @classmethod
    def from_file(cls,
                  client_id: str,
                  client_secret: str = "",
                  file="creds.json",
                  decoded_file: dict = None,
                  callback_url: str = "https://localhost"
                  ):
        if decoded_file is not None:
            content = decoded_file
        else:
            with open(file, "r") as file:
                content = loads(file.read())
        access_token = content[client_id]["access_token"]
        refresh_token = content[client_id]["refresh_token"]
        token_expiry_unix = content[client_id]["unix_expire"]

        auth_class = cls(client_id=client_id, client_secret=client_secret, callback_url=callback_url)
        auth_class._access_token = access_token
        auth_class.refresh_token = refresh_token
        auth_class._token_expiry_unix = token_expiry_unix

        return auth_class

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self._access_token}"}

    def _create_code_challenge(self) -> str:
        self.code_challenge = secrets.token_urlsafe(64)[:127]
        return str(self.code_challenge)

    def get_authorize_url(self, scope: enums.Scopes, code_challenge: str, state: str = None) -> str:
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.callback_url,
            "code_challenge": code_challenge,
            "scope": str(scope)
        }
        if state is not None:
            auth_params["state"] = str(state)

        url = self._make_url(self.auth_url, [self.auth_ver, self.auth_code_path], auth_params)
        return url

    def get_token(self, code: str, code_challenge: str, state: str = None) -> dict:
        token_body = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.callback_url,
            "code_verifier": code_challenge
        }
        if state is not None:
            token_body["state"] = str(state)
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.client_basic}"
        }
        url = self._make_url(self.auth_url, [self.auth_ver, self.auth_token_path])
        req = rq.post(url, data=token_body, headers=token_headers)
        try:
            req.raise_for_status()
        except Exception as e:
            print(req.content, req.headers)
            raise rq.HTTPError(e)

        response = dict(req.json())
        unix_expire_time = self._get_expiry_time_unix(response["expire_in"])
        response["unix_expire"] = unix_expire_time
        return response

    def refresh_token(self, refresh_token: str) -> dict:  # Technically the same as get_token (only the body changes)
        token_body = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self.client_basic}"
        }
        url = self._make_url(self.auth_url, [self.auth_ver, self.auth_token_path])
        req = rq.post(url, data=token_body, headers=token_headers)
        try:
            req.raise_for_status()
        except rq.HTTPError as e:
            print(req.content)
            raise rq.HTTPError(e)

        response = dict(req.json())
        unix_expire_time = self._get_expiry_time_unix(response["expire_in"])
        response.update({"unix_expire": unix_expire_time})
        return response


class APIAuth(BaseAuth):
    def __init__(self, client_id: str):
        super().__init__(client_id=client_id, token_type=enums.TokenType.API_KEY)
        self._access_token = client_id

    @property
    def auth_header(self):
        return {"X-MAL-CLIENT-ID": self.client_id}
