import socket
import threading
import datetime

HOST = '127.0.0.1'
PORT = 1733

def handle_client(client_socket):
    try:
        request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request_data:
            client_socket.close()
            return
        
        first_line = request_data.split('\r\n')[0]
        if not first_line.startswith('GET '):
            client_socket.close()
            return

        parts = first_line.split(' ')
        method = parts[0]
        raw_url = parts[1]
        http_version = parts[2]

        if raw_url.startswith('/'):
            raw_url = raw_url[1:]

        http_pos = raw_url.find("://")
        if http_pos != -1:
            raw_url = raw_url[http_pos+3:]
        
        slash_pos = raw_url.find("/")
        if slash_pos == -1:
            slash_pos = len(raw_url)
        host = raw_url[:slash_pos]
        path = raw_url[slash_pos:] or "/"

        new_first_line = f"{method} {path} {http_version}"
        request_data = request_data.replace(first_line, new_first_line, 1)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, 80))
        server_socket.sendall(request_data.encode('utf-8'))

        first_response_chunk = server_socket.recv(4096)
        if first_response_chunk:
            status_line = first_response_chunk.split(b'\r\n', 1)[0]
            status_parts = status_line.split(b' ')
            if len(status_parts) >= 2 and status_parts[0].startswith(b'HTTP/'):
                response_code = status_parts[1].decode('utf-8', errors='ignore')
            else:
                response_code = 'UNKNOWN'

            with open("proxy_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.datetime.now()} | URL: http://{host}{path} | CODE: {response_code}\n")

            client_socket.sendall(first_response_chunk)

            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

        server_socket.close()

    except Exception as e:
        print("Ошибка в handle_client:", e)
    finally:
        client_socket.close()



# python lab04/proxy_server.py



def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((HOST, PORT))
    proxy_socket.listen(50)
    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        client_socket, addr = proxy_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    start_proxy()
