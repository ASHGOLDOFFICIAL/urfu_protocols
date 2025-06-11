from json import JSONDecodeError
import sys

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class AuthData:
    server: str
    port: int
    username: str
    password: str


def read_auth_data(path: Path) -> AuthData | None:
    try:
        with open(path, 'r') as f:
            data = json.load(f)

            return AuthData(
                server=data['server'],
                port=data['port'],
                username=data['username'],
                password=data['password'])
    except JSONDecodeError:
        print("Bad JSON", file=sys.stderr)
    except KeyError:
        print("Incorrect auth file content", file=sys.stderr)
    except FileNotFoundError:
        print("Auth file not found", file=sys.stderr)
