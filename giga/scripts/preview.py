"""Local preview with support for cached extensionless HTML addresses."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.resolve_html()
        super().do_GET()

    def do_HEAD(self):
        self.resolve_html()
        super().do_HEAD()

    def resolve_html(self):
        path = urlsplit(self.path).path
        target = Path(self.translate_path(path))
        if not target.exists() and not target.suffix:
            if Path(str(target) + ".html").is_file():
                self.path = path + ".html"

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    handler = partial(PreviewHandler, directory=str(root))
    ThreadingHTTPServer(("127.0.0.1", 5177), handler).serve_forever()
