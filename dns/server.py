import socket
from dnslib import DNSRecord, QTYPE
from dns.cache import DNSCache


class DNSServer:
    def __init__(self, ip, port, remote_dns_server_ip):
        self._dns_server_ip = ip
        self._port = port
        self._dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._remote_dns_server = socket.socket(socket.AF_INET,
                                                socket.SOCK_DGRAM)
        self._remote_dns_server_ip = remote_dns_server_ip

        self.cache = DNSCache()

    def run(self):
        with self._dns_server, self._remote_dns_server:
            self._dns_server.bind((self._dns_server_ip, self._port))
            while True:
                try:
                    data, addr = self._dns_server.recvfrom(512)
                    self._handle_request(data, addr)
                except Exception as e:
                    print(f"Error: {e}")

    def _handle_request(self, data, addr):
        try:
            query = DNSRecord.parse(data)
            qname = str(query.q.qname)
            qtype = query.q.qtype

            if qtype == QTYPE.PTR and qname == "1.0.0.127.in-addr.arpa.":
                return

            cached = self.cache.get(qname, qtype)

            if cached:
                print(f"Cache hit...")
                response = self._build_response(query, cached)
                print(response, '\n')
                self._dns_server.sendto(response.pack(), addr)
                return

            print(f"Cache miss...")

            try:
                self._remote_dns_server.settimeout(5)
                self._remote_dns_server.sendto(data, (
                    self._remote_dns_server_ip, 53))
                response_data, _ = self._remote_dns_server.recvfrom(512)
                response = DNSRecord.parse(response_data)

                print(response, '\n')

                if response.rr:
                    ttl = response.rr[0].ttl
                    self.cache.put(qname, qtype, response.rr, ttl)
                self._dns_server.sendto(response_data, addr)

            except socket.timeout:
                print(f"Timeout...")
        except Exception as e:
            print(f"Error...")

    def _build_response(self, query, records):
        response = query.reply()
        for rr in records:
            response.add_answer(rr)
        return response
