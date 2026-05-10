import socket

def choose_port(candidates=(8000,8001,8002,8003)):
    for p in candidates:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return 8000
