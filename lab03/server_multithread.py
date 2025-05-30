import socket
import os
import mimetypes
import threading
import sys

def guess_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'

    return mime_type

def handle_client(client_socket, client_address):
    print(f"[+] Новый поток запущен для клиента: {client_address}")

    try:
        request_data = client_socket.recv(1024)
        if not request_data:
            client_socket.close()
            print(f"[-] Соединение с клиентом {client_address} закрыто.")
            return
        
        print(f"Получены данные от {client_address}: {request_data.decode('utf-8', errors='replace')}")

        request_text = request_data.decode('utf-8', errors='replace')

        lines = request_text.split('\r\n')
        request_line = lines[0]
        parts = request_line.split()

        if len(parts) < 2:
            client_socket.close()
            print(f"[-] Соединение с клиентом {client_address} закрыто.")
            return
        
        method, raw_path = parts[0], parts[1]

        if method != 'GET':
            response_405 = (
                "HTTP/1.1 405 Method Not Allowed\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "\r\n"
                "<html><body><h1>405 Method Not Allowed</h1></body></html>"
            )
            client_socket.sendall(response_405.encode('utf-8'))
            client_socket.close()
            print(f"[-] Соединение с клиентом {client_address} закрыто.")
            return

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
            client_socket.close()
            print(f"[-] Соединение с клиентом {client_address} закрыто.")
            return

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

    except Exception as e:
        print(f"Ошибка при работе с клиентом {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[-] Соединение с клиентом {client_address} закрыто.")



def main():
    port = 7000


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)

    print(f"Сервер запущен. Ожидает клиентов на порту {port}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Подключился клиент с адресом: {client_address}")

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

            print(f"[i] Текущее число потоков: {threading.active_count()}")

    except KeyboardInterrupt:
        print("\n[!] Остановка сервера по Ctrl+C")
    finally:
        server_socket.close()
        print("[!] Сервер остановлен.")


if __name__ == "__main__":
    main()