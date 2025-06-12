import pathlib
import sys

import argparse

from proxy.server import FilteringProxyServer


def _main(args: argparse.Namespace):
    domains: list[str] = []
    if args.filter is not None:
        try:
            with open(args.filter, 'r') as f:
                domains = f.readlines()
        except FileNotFoundError:
            parser.error("Filter file doesn't exist")

    server = FilteringProxyServer(filter_domain=domains, port=args.port)
    try:
        server.start()
    except Exception as e:
        print(f"Couldn't start proxy server: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="HTTP Proxy"
    )
    parser.add_argument(
        "--port", '-p',
        type=int,
        default=8080,
        help="Port to run on"
    )
    parser.add_argument(
        '--filter', '-f',
        type=pathlib.Path,
        help="Path to file with domains for filtering"
    )
    _main(parser.parse_args())
