"""Sert un dossier de test sous /carnet-thailande-/ (comme GitHub Pages) : python3 serve_any.py PORT DOSSIER"""
import http.server, os, sys
PORT = int(sys.argv[1]); ROOT = sys.argv[2]
PREFIX = "/carnet-thailande-/"
class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if not path.startswith(PREFIX):
            return os.path.join(ROOT, "__nope__")
        return os.path.join(ROOT, path[len(PREFIX):] or "index.html")
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
