import pathlib
import sys

import socket
from socket import SocketIO
import ssl
from typing import BinaryIO, Callable


class EmailReceiver:
    def __init__(self,
                 username: str, password: str,
                 server: str, port: int):
        self._server = server
        self._port = port
        self._username = username
        self._password = password

    def list(self):
        def _action(sock: BinaryIO):
            list_response = self._send(sock,
                                       'LIST',
                                       multiline=True)
            print(list_response)

        self._session(_action)

    def top(self, index: int, lines: int):
        def _action(sock: BinaryIO):
            headers = self._send(sock,
                                 f'TOP {index} {lines}',
                                 multiline=True)
            print(headers)

        self._session(_action)

    def retrieve(self, index: int, outfile: pathlib.Path):
        def _action(sock: BinaryIO):
            message = self._send(sock,
                                 f'RETR {index}',
                                 multiline=True)
            with open(outfile, "w") as f:
                f.write(message)

        self._session(_action)

    def _session(self, action: Callable[[BinaryIO], None]):
        context = ssl.create_default_context()
        with socket.create_connection((self._server, self._port)) as sock:
            with context.wrap_socket(sock,
                                     server_hostname=self._server) as ssl_sock:
                ssl_sock = ssl_sock.makefile('rwb')
                print(self._readline(ssl_sock), file=sys.stderr)
                self._authenticate(ssl_sock)
                action(ssl_sock)
                self._send(ssl_sock, 'QUIT')

    def _authenticate(self, sock: BinaryIO):
        self._send(sock, f'USER {self._username}')
        self._send(sock, f'PASS {self._password}')

    def _readline(self, sock: BinaryIO) -> str:
        line = sock.readline()
        return line.decode(errors='ignore')

    def _readlines(self, sock: BinaryIO) -> str:
        lines = []
        while True:
            line = sock.readline()
            if not line or line == b'.\r\n':
                break
            lines.append(line)
        response = b''.join(lines).decode(errors='ignore')
        return response

    def _send(self, sock: BinaryIO, cmd: str, multiline: bool = False) -> str:
        sock.write((cmd + '\r\n').encode())
        sock.flush()
        return self._readlines(sock) if multiline else self._readline(sock)
