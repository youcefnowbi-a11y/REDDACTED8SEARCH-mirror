import os
WS = r"C:\Users\PC\OneDrive\Desktop\FOR REDDACTED"
cli = os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinCLI-Linux-x64")
agn = os.path.join(WS, r"RE_Library\05_TARGETS\merlin_extracted\data\bin\merlinAgent-Linux-x64")
b = open(cli, "rb").read()
a = open(agn, "rb").read()
print("SCOPE: merlinCLI-Linux-x64 %d B   merlinAgent-Linux-x64 %d B" % (len(b), len(a)))
print("COUNTED: 2 binaries, 12 probe tokens")
print()

print("=== does the CLI carry an -ldflags -X blob at all? (agent has one at 0x5EE747) ===")
toks = ["-ldflags", "-X main.", "main.psk", "main.sleep",
        "main.httpClient", "merlin", "useragent"]
for tok in toks:
    print("   %-22s CLI=%5d   AGENT=%5d" % (tok, b.count(tok.encode()), a.count(tok.encode())))
print()

print("=== control: strings BOTH should have, to prove the probe works on the CLI ===")
for tok in ["Go build", "runtime.main", "goroutine", "http"]:
    print("   %-22s CLI=%5d   AGENT=%5d" % (tok, b.count(tok.encode()), a.count(tok.encode())))
print()

print("=== the agent config blob in full ===")
seg = a[0x5EE710:0x5EE958]
txt = "".join(chr(c) if 32 <= c < 127 else ("|" if c == 0 else ".") for c in seg)
print(txt)
