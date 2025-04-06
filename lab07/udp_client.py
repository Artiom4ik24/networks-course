import socket
import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
TOTAL_PINGS = 10

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1)

for seq in range(1, TOTAL_PINGS + 1):
    send_time = time.time()
    message = f"Ping {seq} {send_time}"
    try:
        client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        data, server_addr = client_socket.recvfrom(1024)
        recv_time = time.time()

        rtt = recv_time - send_time
        print(f"Ответ от сервера: {data.decode()} | RTT: {rtt:.6f} сек")

    except socket.timeout:
        print("Request timed out")

client_socket.close()
