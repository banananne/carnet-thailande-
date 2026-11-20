"""Sert web/ sous /carnet-thailande-/ comme GitHub Pages (avec compression gzip pour mesurer comme en vrai)."""
import http.server, os, sys, mimetypes, functools
ROOT = "/home/claude/site_en_ligne/web"
PREFIX = "/carnet-thailande-/"
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path == PREFIX[:-1]:
            return os.path.join(ROOT, "__redir__")
        if not path.startswith(PREFIX):
            return os.path.join(ROOT, "__nope__")
        rel = path[len(PREFIX):] or "index.html"
        return os.path.join(ROOT, rel)
    def end_headers(self):
        self.send_header("Cache-Control", "max-age=600")
        super().end_headers()
    def log_message(self, *a): pass
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
