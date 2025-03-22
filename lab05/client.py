#!/usr/bin/env python3

import socket
import sys

HOST = "127.0.0.1"
PORT = 5000

def main():
    command = "dir"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode("utf-8"))
        
        data = s.recv(4096)
    
    print("=== SERVER OUTPUT ===")
    print(data.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
