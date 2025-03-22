import socket

def main():
    PORT = 5005

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", PORT))

        print(f"Listening for broadcast messages on port {PORT} ...")

        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode("utf-8", errors="replace")
            print(f"Received from {addr}: {message}")


if __name__ == "__main__":
    main()