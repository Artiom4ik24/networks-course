import socket
import sys

def is_port_free(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        return result != 0

def scan_free_ports(ip, start_port, end_port):
    print(f"\nСвободные порты на {ip} в диапазоне {start_port}-{end_port}:\n")
    for port in range(start_port, end_port + 1):
        if is_port_free(ip, port):
            print(f"Порт {port} — свободен")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python free_ports.py <IP-адрес> <диапазон портов, напр. 20-80>")
        sys.exit(1)

    ip_address = sys.argv[1]
    port_range = sys.argv[2]
    start_port, end_port = map(int, port_range.split("-"))

    scan_free_ports(ip_address, start_port, end_port)
