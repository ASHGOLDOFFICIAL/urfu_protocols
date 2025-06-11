import sys

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Config:
    offset_seconds: float
    upstream_server: str
    listen_port: int


def read_config(path: Path) -> Config | None:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return Config(offset_seconds=data["offset_seconds"],
                          upstream_server=data["upstream_server"],
                          listen_port=data["listen_port"])
    except KeyError:
        print("Incorrect config file content", file=sys.stderr)
    except FileNotFoundError:
        print("Config file not found", file=sys.stderr)