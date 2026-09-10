#!/usr/bin/env python3
"""Serve the Pinned Orrery on localhost."""
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import os, sys
os.chdir(Path(__file__).resolve().parent)
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
print(f"PINNED ORRERY → http://127.0.0.1:{port}/")
HTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler).serve_forever()
