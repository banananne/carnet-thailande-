# -*- coding: utf-8 -*-
"""Point d'entrée : python3 build.py  →  web/ (prêt à publier)."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site

if __name__ == "__main__":
    build_site.build_web()
