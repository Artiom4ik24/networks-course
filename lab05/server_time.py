#!/usr/bin/env python3

import socket
import time

def main():
    BROADCAST_IP = "<broadcast>"
    PORT = 5005

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            sock.sendto(current_time.encode("utf-8"), (BROADCAST_IP, PORT))

            print(f"Broadcasted: {current_time}")
            time.sleep(1)


if __name__ == "__main__":
    main()
