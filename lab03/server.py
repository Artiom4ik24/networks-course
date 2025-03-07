import socket
import os
import mimetypes
import sys

def guess_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    return mime_type

def main():
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Ошибка: неправильный порт.")
            sys.exit(1)
    else:
        port = 7000


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen()

    print('Сервер успешно запущен и ожидает соединения...')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Подключился клиент с адресом: {client_address}")

        with client_socket:
            request_data = client_socket.recv(1024)

            if not request_data:
                continue

            request_text = request_data.decode('utf-8', errors='replace')
            print("Получен запрос:\n", request_text)

            lines = request_text.split('\r\n')
            request_line = lines[0]
            parts = request_line.split()

            if len(parts) < 2:
                continue
            
            method, raw_path = parts[0], parts[1]

            if method != 'GET':
                response_405 = (
                    "HTTP/1.1 405 Method Not Allowed\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "\r\n"
                    "<html><body><h1>405 Method Not Allowed</h1></body></html>"
                )
                client_socket.sendall(response_405.encode('utf-8'))
                continue

            if raw_path.startswith('/'):
                    raw_path = raw_path[1:]

            if not os.path.isfile(raw_path):
                not_found_response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "\r\n"
                    "<html>"
                    "<head><title>404 Not Found</title></head>"
                    "<body><h1>404 - Файл не найден</h1></body>"
                    "</html>"
                )
                client_socket.sendall(not_found_response.encode('utf-8'))
                continue

            with open(raw_path, 'rb') as f:
                content = f.read()

            content_type = guess_mime_type(raw_path)

            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(response_headers.encode('utf-8'))
            client_socket.sendall(content)


if __name__ == "__main__":
    main()