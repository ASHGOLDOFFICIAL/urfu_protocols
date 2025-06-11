import sys
import argparse
import pathlib
from sntp.config import read_config
from sntp.server import SNTPLiarServer


def _main(args: argparse.Namespace):
    config = read_config(args.config)
    if config is None:
        sys.exit(1)
    server = SNTPLiarServer(
        offset_seconds=config.offset_seconds,
        upstream_server=config.upstream_server,
        listen_port=config.listen_port
    )
    server.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SNTP Liar Server"
    )
    parser.add_argument(
        "config",
        type=pathlib.Path,
        help="Path to config file"
    )
    _main(parser.parse_args())
