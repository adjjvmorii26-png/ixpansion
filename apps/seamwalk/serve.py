#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import os, sys, subprocess
os.chdir(Path(__file__).resolve().parent)
subprocess.run([sys.executable, "build_seams.py"], check=False)
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
print(f"SEAMWALK → http://127.0.0.1:{port}/")
HTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler).serve_forever()
