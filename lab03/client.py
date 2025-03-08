import sys
import socket

def main():
    if len(sys.argv) != 4:
        print("Использование: python client.py <server_host> <server_port> <filename>")
        sys.exit(1)
    
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, server_port))

        request = (
            f"GET /{filename} HTTP/1.1\r\n"
            f"Host: {server_host}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        s.sendall(request.encode('utf-8'))

        response_data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response_data += chunk
        
    print(response_data.decode('utf-8', errors='replace'))

if __name__ == "__main__":
    main()
