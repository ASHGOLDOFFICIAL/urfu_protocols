from email.header import Header
import mimetypes
from pathlib import Path
import quopri
import socket
import ssl
import base64
import uuid

from smtp.email import Email


class EmailSender:
    def __init__(self,
                 username: str, password: str,
                 server: str, port: int):
        self._server = server
        self._port = port
        self._sender = username
        self._username = base64.b64encode(username.encode()).decode()
        self._password = base64.b64encode(password.encode()).decode()

    def send(self, email: Email):
        prepared = self._create_mime_message(email)

        with socket.create_connection((self._server, self._port)) as sock:
            resp = sock.recv(4096).decode()
            print(f"S: {resp.strip()}")
            if not resp.startswith("220"):
                raise Exception("Failed to connect")

            self._send_cmd(sock,
                           f"EHLO {socket.gethostname()}",
                           expect_code=250)
            self._send_cmd(sock,
                           "STARTTLS",
                           expect_code=220)

            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=self._server)
            print("TLS connection established")

            self._send_cmd(sock,
                           f"EHLO {socket.gethostname()}",
                           expect_code=250)

            self._authenticate(sock)

            self._send_cmd(sock,
                           f"MAIL FROM:<{self._sender}>",
                           expect_code=250)

            for rcpt in email.recipients:
                self._send_cmd(sock, f"RCPT TO:<{rcpt}>", expect_code=250)

            self._send_cmd(sock, "DATA", expect_code=354)
            sock.sendall((prepared + "\r\n.\r\n").encode('utf-8'))

            resp = sock.recv(4096).decode()
            print(f"S: {resp.strip()}")
            if not resp.startswith("250"):
                raise Exception("Failed to send message data")
            self._send_cmd(sock, "QUIT", expect_code=221)

        print("Email sent successfully")

    def _authenticate(self, sock: socket.socket):
        self._send_cmd(sock, "AUTH LOGIN", expect_code=334)
        self._send_cmd(sock, self._username, expect_code=334)
        self._send_cmd(sock, self._password, expect_code=235)

    def _send_cmd(self,
                  sock: socket.socket,
                  cmd: str, expect_code=None) -> str:
        print(f"C: {cmd}")
        sock.sendall((cmd + "\r\n").encode())
        resp = sock.recv(4096).decode()
        print(f"S: {resp.strip()}")
        if expect_code and not resp.startswith(str(expect_code)):
            raise Exception(f"Unexpected response: {resp}")
        return resp

    def _create_mime_message(self, email: Email) -> str:
        boundary = str(uuid.uuid4())

        body = email.content
        lines = [f"From: {str(Header(self._sender, 'utf-8'))}",
                 f"To: {', '.join(email.recipients)}",
                 f"Subject: {str(Header(email.subject, 'utf-8'))}",
                 "MIME-Version: 1.0",
                 f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n',
                 f"--{boundary}",
                 "Content-Type: text/plain; charset=utf-8",
                 "Content-Transfer-Encoding: quoted-printable",
                 "",
                 quopri.encodestring(body.encode('utf-8')).decode('ascii'),
                 ""]

        for path in email.attachments:
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()

            filename = Path(path).name

            lines += [
                f"--{boundary}",
                f"Content-Type: {mime_type}; name=\"{filename}\"",
                "Content-Transfer-Encoding: base64",
                f"Content-Disposition: attachment; filename=\"{filename}\"",
                ""
            ]

            for i in range(0, len(data), 76):
                lines.append(data[i:i + 76])
            lines.append("")

        lines += [
            f"--{boundary}--",
            ""
        ]

        return "\r\n".join(lines)
