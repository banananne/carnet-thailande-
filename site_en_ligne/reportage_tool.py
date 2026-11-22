# -*- coding: utf-8 -*-
"""Reportage photo des invité·e·s : outil de publication (jamais publié lui-même).

Les polaroïds faits par les voyageurs (onglet « Photo pour les invités ») sont CHIFFRÉS ici avec le code des invité·e·s
(PBKDF2-SHA256 150 000 tours, puis AES-GCM, comme les enveloppes secrètes) et rangés dans le dossier `reportage/` du générateur :
    reportage/m.json     la liste (date, prénom, fichier de chaque photo), chiffrée
    reportage/pXXXXXXXX.bin   une photo = IV (12 octets) + texte chiffré ; données associées « rep|pXXXXXXXX »
Le site publié contient ces fichiers tels quels : sans le code, on ne voit rien. Le code n'est JAMAIS écrit dans le dépôt :
il est lu dans /home/claude/prive/code_invites.txt (ou donné avec --code pour un essai).

Usage (depuis /home/claude/site_en_ligne) :
    python3 -I reportage_tool.py add  --date 2026-12-20 --who Anne  photo1.jpg photo2.jpg
    python3 -I reportage_tool.py list
    python3 -I reportage_tool.py rm   pXXXXXXXX
    python3 -I reportage_tool.py clear            (vide tout le reportage : retire le dossier reportage/)
Options : --dir DOSSIER (défaut reportage/), --code-file FICHIER, --code CODE (essai uniquement).
"""
import argparse, base64, json, os, re, secrets, shutil, sys, unicodedata
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(HERE, "reportage")
CODE_FILE = "/home/claude/prive/code_invites.txt"
ITER = 150000
WHO = ("Arthur", "Daphne", "Flo", "Anne")


def b64(b):
    return base64.b64encode(b).decode("ascii")


def norm(code):
    """Même règle que dans photo.js : sans accents ni majuscules, lettres et chiffres seulement."""
    s = unicodedata.normalize("NFD", code.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def key_for(code, salt):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(norm(code).encode("utf-8"))


def read_code(args):
    if args.code:
        return args.code
    with open(args.code_file, encoding="utf-8") as f:
        c = f.read().strip()
    assert norm(c) and len(norm(c)) >= 6, "code trop court"
    return c


def load(d, code):
    """→ (sel, liste) ; (None, []) si le reportage n'existe pas encore."""
    p = os.path.join(d, "m.json")
    if not os.path.exists(p):
        return None, []
    m = json.load(open(p, encoding="utf-8"))
    salt = base64.b64decode(m["s"])
    pt = AESGCM(key_for(code, salt)).decrypt(base64.b64decode(m["iv"]), base64.b64decode(m["ct"]), b"rep|m")
    return salt, json.loads(pt.decode("utf-8"))["p"]


def save_manifest(d, code, salt, items):
    iv = secrets.token_bytes(12)
    pt = json.dumps({"p": items}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ct = AESGCM(key_for(code, salt)).encrypt(iv, pt, b"rep|m")
    json.dump({"v": 1, "it": ITER, "s": b64(salt), "iv": b64(iv), "ct": b64(ct)}, open(os.path.join(d, "m.json"), "w"), separators=(",", ":"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "list", "rm", "clear"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--code-file", default=CODE_FILE)
    ap.add_argument("--code")
    ap.add_argument("--date")
    ap.add_argument("--who")
    args = ap.parse_args()
    d = args.dir
    if args.cmd == "clear":
        if os.path.isdir(d):
            shutil.rmtree(d)
        print("reportage vidé :", d)
        return
    code = read_code(args)
    salt, items = load(d, code)
    if args.cmd == "list":
        for it in items:
            print(it["f"], it["d"], it["w"])
        print(len(items), "photo(s)")
        return
    if args.cmd == "rm":
        keep = [it for it in items if it["f"] not in args.files]
        assert len(keep) == len(items) - len(args.files), "identifiant inconnu"
        for f in args.files:
            os.remove(os.path.join(d, f + ".bin"))
        save_manifest(d, code, salt, keep)
        print("retiré :", args.files)
        return
    assert args.date and re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date), "--date AAAA-MM-JJ"
    assert args.who in WHO, "--who : " + ", ".join(WHO)
    assert args.files, "aucune photo"
    os.makedirs(d, exist_ok=True)
    if salt is None:
        salt = secrets.token_bytes(16)
    key = AESGCM(key_for(code, salt))
    for p in args.files:
        raw = open(p, "rb").read()
        assert raw[:3] == b"\xff\xd8\xff" or raw[:8] == b"\x89PNG\r\n\x1a\n" or raw[:4] == b"RIFF", p + " : ni JPEG, ni PNG, ni WebP"
        fid = "p" + secrets.token_hex(4)
        iv = secrets.token_bytes(12)
        open(os.path.join(d, fid + ".bin"), "wb").write(iv + key.encrypt(iv, raw, ("rep|" + fid).encode("ascii")))
        items.append({"f": fid, "d": args.date, "w": args.who})
        print("ajouté", fid, args.date, args.who, "(%d Ko)" % (len(raw) // 1024))
    save_manifest(d, code, salt, items)


if __name__ == "__main__":
    main()
