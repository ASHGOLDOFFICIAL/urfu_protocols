from bs4 import BeautifulSoup


class LinkRemoverPageParser:
    def parse(self, content: str):
        try:
            soup = BeautifulSoup(content, "html.parser")
            for a_tag in soup.find_all("a"):
                a_tag.decompose()
            return soup.encode()
        except Exception as e:
            print(f"HTML parsing error: {e}")
            return content