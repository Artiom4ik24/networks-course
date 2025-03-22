#!/usr/bin/env python3

import socket
import subprocess

HOST = "127.0.0.1"
PORT = 5000

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((HOST, PORT))
        server_sock.listen(1)
        print(f"[+] Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_sock.accept()
            print(f"[+] Connected by {addr}")
            with conn:
                data = conn.recv(4096)
                if not data:
                    continue
                command = data.decode("utf-8", errors="replace").strip()
                print(f"[+] Received command: {command}")

                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    output = str(e).encode("utf-8")

                conn.sendall(output)
            print("[+] Connection closed\n")

if __name__ == "__main__":
    main()
