"""Local RCON utility. Reads credentials from run/server.properties, never argv."""
import socket
import struct
import sys
from pathlib import Path

def properties(path):
    return dict(line.split("=", 1) for line in path.read_text().splitlines()
                if "=" in line and not line.lstrip().startswith("#"))

def exact(sock, count):
    data = b""
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise ConnectionError("RCON connection closed")
        data += chunk
    return data

def packet(sock):
    size, = struct.unpack("<i", exact(sock, 4))
    if not 10 <= size <= 4 * 1024 * 1024:
        raise ValueError("Invalid RCON packet length")
    data = exact(sock, size)
    ident, kind = struct.unpack("<ii", data[:8])
    return ident, kind, data[8:-2].decode("utf-8", errors="replace")

def send(sock, ident, kind, text):
    data = struct.pack("<ii", ident, kind) + text.encode() + b"\0\0"
    sock.sendall(struct.pack("<i", len(data)) + data)

def command(text, run=None):
    run = run or Path(__file__).resolve().parent / "run"
    config = properties(run / "server.properties")
    with socket.create_connection(("127.0.0.1", int(config.get("rcon.port", 25575))), 10) as sock:
        sock.settimeout(30)
        send(sock, 1, 3, config["rcon.password"])
        while True:
            ident, kind, _ = packet(sock)
            if ident == -1:
                raise PermissionError("RCON authentication failed")
            if kind == 2:
                break
        send(sock, 2, 2, text)
        # Empty command is an ordered fence for multi-packet command responses.
        send(sock, 3, 2, "")
        result = []
        while True:
            ident, _, body = packet(sock)
            if ident == 3:
                return "".join(result)
            if ident == 2:
                result.append(body)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path)
    parser.add_argument("commands", nargs="+")
    args = parser.parse_args()
    for text in args.commands:
        print(command(text, args.run))
