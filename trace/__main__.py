import ipaddress

import argparse
from dataclasses import dataclass
from ipaddress import IPv4Address
import os
import re
from tabulate import tabulate
from requests import get

BAD_IP_REGEX: re.Pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
IPAPI_URL = 'http://ip-api.com/json/{}?fields=status,country,isp,as'


@dataclass
class IpInfo:
    ip: IPv4Address
    country: str | None
    isp: str | None
    asn: str | None


def _get_ip_info_from_ipapi(ip: IPv4Address) -> IpInfo | None:
    response: dict = get(IPAPI_URL.format(ip)).json()
    if response.get("status") == "success":
        return IpInfo(ip=ip,
                      country=response.get("country"),
                      isp=response.get("isp"),
                      asn=response.get("as"))
    return None


def _get_ip_info(ip: IPv4Address) -> IpInfo:
    if ip.is_private:
        return IpInfo(ip=ip,
                      country='Private IP',
                      isp='Private IP',
                      asn='Private IP')
    try:
        info: IpInfo | None = _get_ip_info_from_ipapi(ip)
        if info is not None:
            return info
        return IpInfo(ip, None, None, None)
    except Exception as e:
        print(e)
        return IpInfo(ip, None, None, None)


def _trace_route(ip: IPv4Address) -> list[IPv4Address]:
    p = os.popen(f'traceroute {ip} | tail -n+2')
    output: str = p.read()
    return [IPv4Address(x) for x in BAD_IP_REGEX.findall(output)]


def _print_ip_info_table(ips: list[IpInfo]) -> None:
    t: str = tabulate(ips,
                      headers=["ip", "country", "ips", "as"],
                      tablefmt='fancy_grid')
    print(t)


def main(args: argparse.Namespace):
    try:
        dest: IPv4Address = IPv4Address(args.ip)
    except ipaddress.AddressValueError as e:
        print("Incorrect IPv4 address")
        exit(1)
    route: list[IPv4Address] = _trace_route(dest)
    ipinfo = [_get_ip_info(ip) for ip in route]
    _print_ip_info_table(ipinfo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tracer"
    )
    parser.add_argument(
        "ip",
        type=str,
        help="Input IPv4 address"
    )
    main(parser.parse_args())
