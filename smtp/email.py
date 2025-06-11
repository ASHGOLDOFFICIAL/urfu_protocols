from json import JSONDecodeError
import pathlib
import sys

from dataclasses import dataclass
import json
from pathlib import Path
from smtp.utils import read_file_content


@dataclass
class Email:
    subject: str
    recipients: list[str]
    content: str
    attachments: list[pathlib.Path]


def read_email_description(path: Path) -> Email | None:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            
            config_dir = path.parent
            content = read_file_content(config_dir / data["content"])
            attachments = [config_dir / a for a in data["attachments"]]
            
            return Email(subject=data["subject"],
                         recipients=data["recipients"],
                         content=content,
                         attachments=attachments)
    except JSONDecodeError:
        print("Bad JSON", file=sys.stderr)
    except KeyError:
        print("Incorrect email description file content", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"Some files do not exist: {e}", file=sys.stderr)