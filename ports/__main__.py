import enum

import argparse
import ipaddress
from ipaddress import IPv4Address
from tabulate import tabulate
from ports.detector import DetectionResult, ProtocolDetector


class Protocol(enum.StrEnum):
    TCP = "tcp"
    UDP = "udp"


def _main(args: argparse.Namespace):
    try:
        dest: IPv4Address = IPv4Address(args.ip)
    except ipaddress.AddressValueError:
        parser.error("Invalid IPv4 address.")
    start: int = args.port_start
    end: int = args.port_end

    protocol_detector = ProtocolDetector(args.timeout)
    protocols: dict[int, DetectionResult] = {}

    if args.protocol == Protocol.TCP:
        protocols = protocol_detector.detect_tcp_protocols(dest, start, end)
    elif args.protocol == Protocol.UDP:
        protocols = protocol_detector.detect_udp_protocols(dest, start, end)
    
    result = [(port, protocol.name) for port, protocol in protocols.items()]
    t: str = tabulate(sorted(result, key=lambda x: x[0]),
                      headers=["port", "protocol"])
    print(t)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Port Scanner"
    )
    parser.add_argument(
        "protocol",
        type=str,
        choices=[str(protocol) for protocol in Protocol],
        help="Protocol to use"
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
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=0.5,
        help="How long to wait for a reply"
    )
    _main(parser.parse_args())
