import argparse
import ipaddress
from ipaddress import IPv4Address

from port_scanner.scanner import PortScanner


def _main(args: argparse.Namespace):
    try:
        dest: IPv4Address = IPv4Address(args.ip)
    except ipaddress.AddressValueError as e:
        print("Incorrect IPv4 address")
        exit(1)
    start: int = args.port_start
    end: int = args.port_end

    port_scanner = PortScanner()
    ports = []
    if args.protocol == "tcp":
        ports = port_scanner.open_tcp_ports(dest, start, end)
    elif args.protocol == "udp":
        ports = port_scanner.open_udp_ports(dest, start, end)
    print(ports)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Port Scanner"
    )
    parser.add_argument(
        "protocol",
        type=str,
        choices=["tcp", "udp"],
    )
    parser.add_argument(
        "ip",
        type=str,
        help="Input IPv4 address"
    )
    parser.add_argument(
        "port_start",
        type=int,
        help="Port range lower bound"
    )
    parser.add_argument(
        "port_end",
        type=int,
        help="Port range upper bound (non-inclusive)"
    )
    _main(parser.parse_args())
