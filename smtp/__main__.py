import sys

import argparse
import pathlib

from utils.auth import read_auth_data
from smtp.email import read_email_description
from smtp.sender import EmailSender


def _main(args: argparse.Namespace):
    email = read_email_description(args.config)
    if email is None:
        sys.exit(1)
    auth = read_auth_data(args.auth)
    if auth is None:
        sys.exit(1)

    sender = EmailSender(auth.username, auth.password,
                         server=auth.server, port=auth.port)
    sender.send(email)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="SMTP Client"
    )
    parser.add_argument(
        "auth",
        type=pathlib.Path,
        help="Path to authentication data"
    )
    parser.add_argument(
        "config",
        type=pathlib.Path,
        help="Path to config file"
    )
    _main(parser.parse_args())
