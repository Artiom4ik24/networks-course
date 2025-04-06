import socket
import random

SERVER_IP = '0.0.0.0'
SERVER_PORT = 12345
LOSS_PROBABILITY = 0.2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

print(f"UDP-сервер запущен на {SERVER_IP}:{SERVER_PORT}")

while True:
    data, client_addr = sock.recvfrom(1024)
    message = data.decode()

    print(f"Получено сообщение от {client_addr}: {message}")

    if random.random() < LOSS_PROBABILITY:
        print(f"Пакет от {client_addr} утерян.")
        continue

    response = message.upper().encode()
    sock.sendto(response, client_addr)
    
    print(f"Отправлен ответ клиенту {client_addr}: {response.decode()}")
