import sys

import argparse

from dns.server import DNSServer
from threading import Thread


def _input_handler(dns_server: DNSServer):
    while True:
        cmd = input().strip().lower()
        if cmd != 'quit':
            continue
        print("Quiting...")
        dns_server.cache.save_cache()
        sys.exit(0)


def _main(args: argparse.Namespace):
    server: DNSServer = DNSServer(
        args.address,
        args.port,
        '8.8.8.8')
    input_thread: Thread = Thread(
        target=_input_handler,
        args=(server,),
        daemon=True)
    input_thread.start()
    server.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DNS server"
    )
    parser.add_argument(
        "--address", "-a",
        type=str,
        help="Server IP",
        default='127.0.0.1'
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="Server port",
        default=53
    )
    _main(parser.parse_args())
