
import socket

HOST = "0.0.0.0"
PORT = 5001

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"TCP echo server listening on port {PORT}", flush=True)

    while True:
        conn, addr = server.accept()
        print(f"Connected: {addr}", flush=True)

        with conn:
            while True:
                data = conn.recv(4096)

                if not data:
                    break

                conn.sendall(data)
