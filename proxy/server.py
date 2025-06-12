from socketserver import ThreadingTCPServer

from proxy.handler import make_filtering_handler


class FilteringProxyServer:
    def __init__(self, filter_domain: list[str], port: int = 8080):
        self._port = port
        self._filter_domains = filter_domain.copy()
        self._handler = make_filtering_handler(self._filter_domains)
        
    def start(self):
        try:
            with self._ReusableTCPServer(
                    ("", self._port), self._handler) as httpd:
                print(f"Proxy running on port {self._port}")
                if self._filter_domains:
                    print(f'Filtering:',
                          *[d for d in self._filter_domains],
                          sep='\n')
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy server.")
            
    class _ReusableTCPServer(ThreadingTCPServer):
        allow_reuse_address = True