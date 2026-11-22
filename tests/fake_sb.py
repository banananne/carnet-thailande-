"""Faux Supabase (essais seulement) : python3 fake_sb.py PORT. Stockage + table + fonction retirer_photo ; /__ctl/state, /__ctl/fail?n=K (les K prochaines écritures échouent), /__ctl/reset."""
import http.server, json, re, sys, hashlib, uuid, datetime, urllib.parse
PORT = int(sys.argv[1])
ST = {"obj": {}, "rows": [], "fail": 0, "log": []}
KEYS = ("sb_publishable_test",)
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "apikey, authorization, content-type, prefer, x-client-info")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    def out(self, code, body=b"", ct="application/json"):
        if isinstance(body, (dict, list, bool)): body = json.dumps(body).encode()
        self.send_response(code); self.cors(); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self): self.out(204)
    def authed(self): return self.headers.get("apikey") in KEYS
    def body(self): return self.rfile.read(int(self.headers.get("Content-Length") or 0))
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); p = u.path
        if p == "/__ctl/state":
            return self.out(200, {"obj": sorted(ST["obj"]), "sizes": {k: len(v) for k, v in ST["obj"].items()}, "rows": ST["rows"], "log": ST["log"]})
        if p == "/__ctl/reset":
            ST.update(obj={}, rows=[], fail=0, log=[]); return self.out(200, {"ok": 1})
        if p == "/__ctl/fail":
            ST["fail"] = int(urllib.parse.parse_qs(u.query).get("n", ["1"])[0]); return self.out(200, {"ok": 1})
        m = re.fullmatch(r"/storage/v1/object/public/reportage/(.+)", p)
        if m:
            b = ST["obj"].get(m.group(1))
            return self.out(200, b, "application/octet-stream") if b is not None else self.out(404, {"error": "not found"})
        if p == "/rest/v1/reportage":
            if not self.authed(): return self.out(401, {"message": "no key"})
            rows = sorted(ST["rows"], key=lambda r: r["created_at"], reverse=True)
            return self.out(200, [{k: r[k] for k in ("id", "f", "meta", "created_at")} for r in rows])
        self.out(404, {"error": p})
    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path; b = self.body()
        ST["log"].append(p)
        if not self.authed(): return self.out(401, {"message": "no key"})
        if ST["fail"] > 0:
            ST["fail"] -= 1; return self.out(503, {"error": "indisponible"})
        m = re.fullmatch(r"/storage/v1/object/reportage/(p[0-9a-f]{12})", p)
        if m:
            if self.headers.get("Content-Type") != "application/octet-stream": return self.out(415, {"error": "mime"})
            if len(b) > 2097152: return self.out(413, {"error": "trop gros"})
            if m.group(1) in ST["obj"]: return self.out(409, {"error": "existe"})
            ST["obj"][m.group(1)] = b; return self.out(200, {"Key": "reportage/" + m.group(1)})
        if p == "/rest/v1/reportage":
            r = json.loads(b)
            if not (re.fullmatch(r"p[0-9a-f]{12}", r.get("f", "")) and re.fullmatch(r"[0-9a-f]{64}", r.get("del_hash", "")) and len(r.get("meta", "")) < 4000):
                return self.out(400, {"message": "check"})
            if any(x["f"] == r["f"] for x in ST["rows"]): return self.out(409, {"message": "unique"})
            r["created_at"] = datetime.datetime.utcnow().isoformat() + "Z" + str(len(ST["rows"])).zfill(3)
            ST["rows"].append(r); return self.out(201)
        if p == "/rest/v1/rpc/retirer_photo":
            r = json.loads(b); h = hashlib.sha256(r["p_token"].encode()).hexdigest(); n0 = len(ST["rows"])
            ST["rows"] = [x for x in ST["rows"] if not (x["id"] == r["p_id"] and x["del_hash"] == h)]
            return self.out(200, len(ST["rows"]) < n0)
        self.out(404, {"error": p})
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
