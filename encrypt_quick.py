import subprocess, getpass, shutil, os
os.chdir(r"C:\Projects\sms2a-demo")
pwd = getpass.getpass("Enter password: ")
cmd = [
    "npx", "staticrypt",
    r"C:\Projects\document_pipeline\search_v10_5_test.html",
    "-p", pwd,
    "--short", "-d", ".",
    "--template-title", "Arkivklar Document Search",
    "--template-instructions", "SMS-2A · MossIA — Enter password to access",
    "--template-color-primary", "#4B9CD3",
    "--template-color-secondary", "#0D1117",
    "--remember", "30",
]
subprocess.run(cmd, shell=True)
# Rename output
src = r"C:\Projects\sms2a-demo\search_v10_5_test.html"
dst = r"C:\Projects\sms2a-demo\index.html"
if os.path.exists(src):
    shutil.move(src, dst)
    print(f"Done! index.html = {os.path.getsize(dst)//1024} KB")
else:
    print("Output not found — check staticrypt output above")
print("Test with: start index.html")
