"""Encrypt search_v10_5_test.html with StatiCrypt using a password from stdin."""
import subprocess, sys, shutil, getpass
from pathlib import Path

SRC = Path(r"C:\Projects\document_pipeline\search_v10_5_test.html")
OUT_DIR = Path(r"C:\Projects\sms2a-demo")
FINAL = OUT_DIR / "index.html"

if not SRC.exists():
    print(f"ERROR: {SRC} not found — run build_v10_5_test.py first")
    sys.exit(1)

pwd = getpass.getpass("Enter encryption password: ")
if not pwd.strip():
    print("ERROR: empty password")
    sys.exit(1)

cmd = [
    "npx", "staticrypt", str(SRC),
    "-p", pwd,
    "--short",
    "-d", str(OUT_DIR),
    "--template-title", "Arkivklar Document Search",
    "--template-instructions", "SMS-2A MossIA — Enter password to access",
    "--template-color-primary", "#4B9CD3",
    "--template-color-secondary", "#0D1117",
    "--template-placeholder", "Password",
    "--template-button", "DECRYPT",
    "--remember", "30",
]

print(f"Encrypting {SRC.name} ...")
result = subprocess.run(cmd, cwd=str(OUT_DIR), capture_output=True, text=True)

if result.returncode != 0:
    print(f"ERROR: staticrypt failed\n{result.stderr}")
    sys.exit(1)

# staticrypt outputs to OUT_DIR/search_v10_5_test.html — rename to index.html
encrypted = OUT_DIR / SRC.name
if encrypted.exists():
    shutil.move(str(encrypted), str(FINAL))
    size_kb = FINAL.stat().st_size // 1024
    print(f"Done! {FINAL} ({size_kb} KB)")
    print(f"Password: {'*' * len(pwd)} ({len(pwd)} chars)")
else:
    print(f"ERROR: expected {encrypted} but not found")
    print(f"stdout: {result.stdout}")
    sys.exit(1)
