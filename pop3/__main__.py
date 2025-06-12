import enum
import sys

import argparse
import pathlib

from pop3.receiver import EmailReceiver
from utils.auth import read_auth_data


class Commands(enum.StrEnum):
    TOP = "top"
    LIST = "list"
    RETR = "retr"


def _main(args: argparse.Namespace):
    auth = read_auth_data(args.auth)
    if auth is None:
        sys.exit(1)
    receiver = EmailReceiver(auth.username, auth.password,
              server=auth.server, port=auth.port)
    
    match args.command:
        case Commands.LIST:
            receiver.list()
        case Commands.TOP:
            receiver.top(args.index, args.lines)
        case Commands.RETR:
            receiver.retrieve(args.index, args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="POP3 Client"
    )
    parser.add_argument(
        "auth",
        type=pathlib.Path,
        help="Path to authentication data"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        description="Command to execute",
        required=True
    )
    list_parser = subparsers.add_parser(
        Commands.LIST,
        description="List emails"
    )
    
    top_parser = subparsers.add_parser(
        Commands.TOP,
        description="Shows headers and top lines of an email"
    )
    top_parser.add_argument(
        'index',
        type=int,
        help='Email index'
    )
    top_parser.add_argument(
        'lines',
        type=int,
        help='Number of lines'
    )
    
    retr_parser = subparsers.add_parser(
        Commands.RETR,
        help="Retrieves the whole message"
    )
    retr_parser.add_argument(
        'index',
        type=int,
        help='Email index'
    )
    retr_parser.add_argument(
        'output',
        type=pathlib.Path,
        help='Where to save email'
    )
    _main(parser.parse_args())
