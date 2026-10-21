"""Direct client for Blender's lab MCP socket server (localhost:9876).
Protocol: null-byte-delimited JSON {"type":"execute","code":...,"strict_json":bool}.
Code must assign `result` dict. Response is null-byte-delimited JSON.
"""
import socket
import json
import sys

HOST, PORT = "localhost", 9876


def blender_exec(code, strict_json=True, timeout=60):
    req = json.dumps({"type": "execute", "code": code, "strict_json": strict_json}) + "\0"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall(req.encode("utf-8"))
    buf = bytearray()
    while b"\0" not in buf:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf.extend(chunk)
    s.close()
    raw = bytes(buf[:buf.index(b"\0")]) if b"\0" in buf else bytes(buf)
    return json.loads(raw.decode("utf-8"))


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "result = {'hello': 'world'}"
    print(json.dumps(blender_exec(code), indent=1)[:3000])
