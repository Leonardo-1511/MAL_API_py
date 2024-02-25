from pathlib import Path
from json import loads, dumps
from . import auth


class Client:
    def __init__(self,
                 client_id: str,
                 client_secret: str = "",
                 callback_url: str = "http://localhost",
                 filename: str = "creds.json"
                 ):
        if Path(filename).is_file():
            with open(filename, "r") as file:
                creds = dict(loads(file.read()))
            try:
                if client_id in creds:
                    self._existing_file(client_id=client_id, decoded_file=creds, client_secret=client_secret)
            except KeyError:
                raise NotImplementedError

    @classmethod
    def _existing_file(cls, client_id: str, decoded_file: dict, client_secret: str = "", callback_url: str = None):
        if "Authorization" in decoded_file[client_id]["token_type"]:
            cls.auth = auth.MainAuth.from_file(client_id=client_id,
                                               client_secret=client_secret,
                                               decoded_file=decoded_file,
                                               callback_url=callback_url)
            return cls
        elif "api_key" in decoded_file[client_id]["token_type"]:
            cls.auth = auth.APIAuth(client_id=client_id)
            return cls

    def save_file(self, filename="creds.json") -> None:
        base_dict = {
            self.auth.client_id: {
                "token_type": str(self.auth._token_type),
                "unix_expire": self.auth._token_expiry_unix or None,
                "access_token": self.auth._access_token,
                "refresh_token": self.auth.refresh_token or None
            }
        }
        encoded = dumps(base_dict)
        with open(filename, "w") as file:
            file.write(encoded)
        return
