import socket
import struct
import random
import argparse
import os

LOSS_RATE_DEFAULT = 0.3
PACKET_SIZE_DEFAULT = 1024
TIMEOUT_DEFAULT = 0.5

SEQ_DATA_0 = 0
SEQ_DATA_1 = 1
SEQ_FIN    = 2 # eof


def unreliable_sendto(sock: socket.socket, data: bytes, addr):
    if random.random() < LOSS_RATE_DEFAULT:
        print(f'[DROP] {len(data)} bytes')
        return                # симулируем потерю пакета
    sock.sendto(data, addr)


# ------------- CLIENT SIDE ---------------------------------------------------

def client_mode(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    server = (args.host, args.port)
    seq = SEQ_DATA_0

    total_bytes = 0
    with open(args.file, 'rb') as infile:
        while True:
            chunk = infile.read(PACKET_SIZE_DEFAULT)
            if not chunk:
                break
            total_bytes += len(chunk)
            frame = struct.pack('!B', seq) + chunk
            while True:
                unreliable_sendto(sock, frame, server)
                try:
                    ack, _ = sock.recvfrom(1)
                    if ack and ack[0] == seq:
                        print(f'[ACK] seq={seq}')
                        break                     # идём дальше
                except socket.timeout:
                    print(f'[TIMEOUT] resend seq={seq}')
            seq ^= 1                               # меняем 0 на 1 и наоборот

    fin = bytes([SEQ_FIN])
    while True:
        unreliable_sendto(sock, fin, server)
        try:
            ack, _ = sock.recvfrom(1)
            if ack and ack[0] == SEQ_FIN:
                print('[COMPLETE] transfer finished')
                break
        except socket.timeout:
            print('[TIMEOUT] resend FIN')

    sock.close()
    print(f'[STATS] {total_bytes} bytes sent successfully')


# ------------- SERVER SIDE ---------------------------------------------------

def server_mode(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', args.port))
    expected = SEQ_DATA_0
    client_addr = None
    written_bytes = 0

    print(f'[LISTENING] UDP port {args.port}')

    with open(args.out, 'wb') as outfile:
        while True:
            data, addr = sock.recvfrom(PACKET_SIZE_DEFAULT + 1)
            if client_addr is None:
                client_addr = addr
                print(f'[CLIENT] {client_addr} connected')

            if not data:
                continue

            seq = data[0]

            # FIN frame ends the session
            if seq == SEQ_FIN:
                print('[FIN] received from client')
                unreliable_sendto(sock, bytes([SEQ_FIN]), client_addr)
                break

            payload = data[1:]

            if seq == expected:
                outfile.write(payload)
                written_bytes += len(payload)
                expected ^= 1
            else:
                print(f'[DUP] seq={seq} ignored')

            unreliable_sendto(sock, bytes([seq]), client_addr)

    sock.close()
    print(f'[STATS] wrote {written_bytes} bytes to {args.out}')


def main():
    parser = argparse.ArgumentParser(description='Stop‑and‑wait demo over UDP')
    sub = parser.add_subparsers(dest='role', required=True)

    c = sub.add_parser('client', help='run in sender mode')
    c.add_argument('host', help='server ip')
    c.add_argument('port', type=int, help='server UDP port')
    c.add_argument('file', help='file to send')
    c.add_argument('-t', '--timeout', type=float, default=TIMEOUT_DEFAULT,
                   help='socket timeout in seconds')

    # Server
    s = sub.add_parser('server', help='run in receiver mode')
    s.add_argument('port', type=int, help='UDP port to listen on')
    s.add_argument('out', help='output file')
    s.add_argument('-s', '--size', type=int, default=PACKET_SIZE_DEFAULT,
                   help='payload size to expect (bytes)')
    s.add_argument('-l', '--loss', type=float, default=LOSS_RATE_DEFAULT,
                   help='simulated packet loss rate (0–1)')

    args = parser.parse_args()
    random.seed()

    if args.role == 'client':
        client_mode(args)
    else:
        server_mode(args)


if __name__ == '__main__':
    main()
