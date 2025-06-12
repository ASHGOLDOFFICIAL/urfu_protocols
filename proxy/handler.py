from http.server import BaseHTTPRequestHandler
import requests
from urllib.parse import urlparse

from proxy.parser import LinkRemoverPageParser


def make_filtering_handler(domains: list[str]) -> BaseHTTPRequestHandler:
    filter_domains = domains.copy()

    class FilteringProxyRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)

            if parsed_url.scheme == '':
                self.send_error(400, "Full URL required")
                return

            target_url = self.path
            domain = parsed_url.hostname

            try:
                headers = {key: val for key, val in self.headers.items()}

                resp = requests.get(target_url, headers=headers)
                content = resp.content
                content_type = resp.headers.get('Content-Type', '')

                if self._needs_filtering(
                        domain) and 'text/html' in content_type:
                    parser = LinkRemoverPageParser()
                    content = parser.parse(content)

                self.send_response(resp.status_code)
                for key, val in resp.headers.items():
                    if key.lower() in ['content-encoding', 'content-length']:
                        continue
                    self.send_header(key, val)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)

            except Exception as e:
                self.send_error(500, f"Error: {e}")

        def _needs_filtering(self, domain: str) -> bool:
            return any(domain.endswith(d) for d in filter_domains)

    return FilteringProxyRequestHandler
