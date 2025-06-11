import math
import socket
import struct
import ntplib
from datetime import datetime

NTP_TIMESTAMP_DELTA = 2208988800

# Leap Indicator, Version Number, Mode
# 00 (no warning) 100 (version 4, NTPv4) 100 (server)
_LI_VN_MODE = (0 << 6) | (4 << 3) | 4

class SNTPLiarServer:
    def __init__(self,
                 offset_seconds: float,
                 upstream_server: str,
                 listen_port: int):
        self._offset = offset_seconds
        self._upstream = upstream_server
        self._port = listen_port
        self._client = ntplib.NTPClient()

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self._port))
        print(
            f"SNTP Liar Server running on UDP port "
            f"{self._port}, lying by {self._offset} seconds")

        while True:
            try:
                data, addr = sock.recvfrom(48)
                print(f"Received SNTP request from {addr}")

                originate_timestamp = data[40:48]
                if originate_timestamp == b'\x00' * 8:
                    originate_timestamp = struct.pack("!II", 0, 0)

                real_time = self._get_time_from_upstream()
                fake_time = real_time + self._offset

                response = self._build_sntp_packet(originate_timestamp,
                                                   fake_time)
                sock.sendto(response, addr)
                print(
                    f"Sent time: {datetime.utcfromtimestamp(fake_time)} to {addr}")

            except Exception as e:
                print("Error:", e)

    def _get_time_from_upstream(self):
        response = self._client.request(self._upstream, version=3)
        return response.tx_time

    def _build_sntp_packet(self,
                           originate_timestamp: bytes,
                           transmit_time_unix: float):
        transmit_time_ntp = transmit_time_unix + NTP_TIMESTAMP_DELTA
        transmit_timestamp = self._make_timestamp(transmit_time_ntp)
    
        receive_time_ntp = transmit_time_ntp
        receive_timestamp = self._make_timestamp(receive_time_ntp)
    
        ref_time_ntp = transmit_time_ntp - 1
        ref_timestamp = self._make_timestamp(ref_time_ntp)
    
        return struct.pack("!B B B B 11I",
                           _LI_VN_MODE, 2, 0, 0,
                           0, 0, 0,
                           *struct.unpack("!II", ref_timestamp),
                           *struct.unpack("!II", originate_timestamp),
                           *struct.unpack("!II", receive_timestamp),
                           *struct.unpack("!II", transmit_timestamp)
                           )
    
    def _make_timestamp(self, time: float) -> bytes:
        frac, whole = math.modf(time)
        return struct.pack("!II", int(whole), int(frac * 2 ** 32))