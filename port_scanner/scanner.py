from concurrent.futures import ThreadPoolExecutor, as_completed

from ipaddress import IPv4Address
import socket
from typing import Callable


class PortScanner:
    def __init__(self,
                 timeout: float = 0.1,
                 max_workers: int = 100):
        self._timeout = timeout
        self._workers = max_workers

    def open_tcp_ports(self,
                       ip: IPv4Address,
                       start: int, end: int) -> list[int]:
        return self._open_ports(self._is_tcp_port_open, ip, start, end)

    def open_udp_ports(self,
                       ip: IPv4Address,
                       start: int, end: int) -> list[int]:
        return self._open_ports(self._is_udp_port_open, ip, start, end)

    def _open_ports(self,
                    func: Callable[[IPv4Address, int], bool],
                    ip: IPv4Address,
                    start: int, end: int) -> list[int]:
        open_ports = []
        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            futures = {
                executor.submit(
                    func, ip, port): port
                for port in range(start, end)
            }
            for future in as_completed(futures):
                port = futures[future]
                if future.result():
                    open_ports.append(port)
        return sorted(open_ports)

    def _is_tcp_port_open(self, ip: IPv4Address, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                return sock.connect_ex((str(ip), port)) == 0
        except socket.error:
            return False

    def _is_udp_port_open(self, ip: IPv4Address, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self._timeout)
                sock.sendto(b'\x00', (str(ip), port))
                try:
                    sock.recvfrom(1024)
                    return True
                except socket.timeout:
                    return True
        except socket.error:
            return False
