import re
from collections.abc import Iterable

PROTO_RE = re.compile(r'^(?:(https?|socks4|socks5)://)?(.+)$', re.I)


def normalize_proxy(line: str):
    s = line.strip()
    if not s:
        return None
    m = PROTO_RE.match(s)
    if not m:
        return None
    proto, rest = m.groups()
    proto = (proto or "").lower()

    if "@" in rest:
        creds, hostport = rest.split("@", 1)
        if ":" not in hostport:
            return None
        host, port = hostport.rsplit(":", 1)
        if ":" not in creds:
            return None
        user, pwd = creds.split(":", 1)
        fmt = f"{user}:{pwd}@{host}:{port}"
    else:
        parts = rest.split(":")
        if len(parts) == 2:
            host, port = parts
            fmt = f"{host}:{port}"
        elif len(parts) >= 4:
            host, port, user, pwd = parts[0], parts[1], parts[2], ":".join(parts[3:])
            fmt = f"{user}:{pwd}@{host}:{port}"
        else:
            return None
    if not port.isdigit():
        return None
    p = int(port)
    if p < 1 or p > 65535:
        return None
    if not proto:
        proto = "http"
    return proto, fmt


def parse_many(lines: Iterable[str]):
    out = set()
    for line in lines:
        n = normalize_proxy(line)
        if n:
            out.add(n)
    return out
