from concurrent.futures import ThreadPoolExecutor, as_completed

from enum import Enum, auto
from ipaddress import IPv4Address
import random

import socket
import struct
from typing import Callable

_HTTP_TEST = b"GET / HTTP/1.0\r\n\r\n"
_SMTP_TEST = b"EHLO test\r\n"
_POP3_TEST = b"QUIT\r\n"


class DetectionResult(Enum):
    UNKNOWN = auto()
    CLOSED = auto()
    HTTP = auto()
    SMTP = auto()
    POP3 = auto()
    DNS = auto()
    SNTP = auto()


class ProtocolDetector:
    def __init__(self,
                 timeout: float = 0.3,
                 max_workers: int = 100):
        self._timeout = timeout
        self._workers = max_workers

    def detect_tcp_protocols(self,
                             ip: IPv4Address,
                             start: int, end: int
                             ) -> dict[int, DetectionResult]:
        return self._detect_protocols(self.detect_tcp_protocol, ip, start, end)

    def detect_udp_protocols(self,
                             ip: IPv4Address,
                             start: int, end: int
                             ) -> dict[int, DetectionResult]:
        return self._detect_protocols(self.detect_udp_protocol, ip, start, end)

    def detect_tcp_protocol(self,
                            ip: IPv4Address,
                            port: int) -> DetectionResult:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                sock.connect((str(ip), port))

                if self._is_http(sock):
                    return DetectionResult.HTTP
                elif self._is_smtp(sock):
                    return DetectionResult.SMTP
                elif self._is_pop3(sock):
                    return DetectionResult.POP3
                else:
                    return DetectionResult.UNKNOWN
        except socket.error:
            return DetectionResult.CLOSED

    def detect_udp_protocol(self,
                            ip: IPv4Address,
                            port: int) -> DetectionResult:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self._timeout)
                sock.connect((str(ip), port))

                if self._is_sntp(sock):
                    return DetectionResult.SNTP
                elif self._is_dns(sock):
                    return DetectionResult.DNS
                else:
                    return DetectionResult.UNKNOWN
        except socket.error:
            return DetectionResult.CLOSED

    def _detect_protocols(self,
                          func: Callable[[IPv4Address, int], DetectionResult],
                          ip: IPv4Address,
                          start: int, end: int) -> dict[int, DetectionResult]:
        protocols: dict[int, DetectionResult] = {}
        with (ThreadPoolExecutor(max_workers=self._workers) as executor):
            future_to_port = {}

            for port in range(start, end):
                future = executor.submit(func, ip, port)
                future_to_port[future] = port

            for future in as_completed(future_to_port):
                port = future_to_port[future]
                result = future.result()
                if result != DetectionResult.CLOSED:
                    protocols[port] = result
        return protocols

    def _is_http(self, sock: socket.socket) -> bool:
        try:
            sock.sendall(_HTTP_TEST)
            resp = sock.recv(1024)
            return resp and b"HTTP/1." in resp
        except socket.error:
            return False

    def _is_smtp(self, sock: socket.socket) -> bool:
        try:
            banner = sock.recv(1024)
            if b"SMTP" in banner or b"220" in banner:
                return True

            sock.sendall(_SMTP_TEST)
            response = sock.recv(1024)
            return b"250" in response or b"SMTP" in response
        except socket.error:
            return False

    def _is_pop3(self, sock: socket.socket) -> bool:
        try:
            sock.settimeout(self._timeout)

            banner = sock.recv(1024)
            if b"+OK" in banner or b"POP3" in banner:
                return True
    
            sock.sendall(_POP3_TEST)
            response = sock.recv(1024)
            return b"+OK" in response or b"POP3" in response
        except socket.error:
            return False

    def _is_sntp(self, sock: socket.socket) -> bool:
        try:
            packet = b'\x1b' + 47 * b'\0'
            sock.send(packet)
            data = sock.recv(512)
            return data and len(data) == 48
        except socket.error:
            return False
    
    def _is_dns(self, sock: socket.socket) -> bool:
        try:
            transaction_id = random.randint(0, 0xFFFF)
            header = struct.pack(">HHHHHH", transaction_id,
                                 0x0100, 1, 0, 0, 0)
            qname = b''.join([bytes([len(part)]) + part.encode()
                              for part in "google.com".split('.')]) + b'\x00'
            question = struct.pack(">HH", 1, 1)
            packet = header + qname + question
    
            sock.send(packet)
            data = sock.recv(512)
            expected = struct.pack(">H", transaction_id)
            return data and len(data) >= 12 and data[:2] == expected
        except socket.error:
            return False
