import socket
import struct
import random
import argparse
import os
from typing import Optional, Tuple
import sys

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


def send_file(sock: socket.socket, peer: Tuple[str, int], filename: str, timeout: float):
    seq = SEQ_DATA_0
    total = 0
    sock.settimeout(timeout)

    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(PACKET_SIZE_DEFAULT)
            if not chunk:
                break
            total += len(chunk)
            frame = struct.pack('!B', seq) + chunk
            while True:
                unreliable_sendto(sock, frame, peer)
                try:
                    ack, _ = sock.recvfrom(1)
                    if ack and ack[0] == seq:
                        print(f"[ACK] seq={seq}")
                        break
                except (socket.timeout, ConnectionResetError):
                    print(f"[TIMEOUT] resend seq={seq}")
            seq = SEQ_DATA_1 if seq == SEQ_DATA_0 else SEQ_DATA_0

    fin = bytes([SEQ_FIN])
    while True:
        unreliable_sendto(sock, fin, peer)
        try:
            ack, _ = sock.recvfrom(1)
            if ack and ack[0] == SEQ_FIN:
                print("[SEND COMPLETE]", filename)
                break
        except (socket.timeout, ConnectionResetError):
            print("[TIMEOUT] resend FIN")

    print(f"[STATS] sent {total} bytes")


def receive_file(sock: socket.socket, outfile: str, first_timeout = None) -> Tuple[str, int]:
    expected = SEQ_DATA_0
    peer_addr = None
    written = 0

    if first_timeout is not None:
        sock.settimeout(first_timeout)

    with open(outfile, 'wb') as f:
        while True:
            try:
                data, addr = sock.recvfrom(PACKET_SIZE_DEFAULT + 1)
            except (socket.timeout, ConnectionResetError):
                if peer_addr is None:
                    print("[ERROR] timed-out waiting for first packet")
                    sys.exit(1)
                continue

            if peer_addr is None:
                peer_addr = addr
                print(f"[PEER] {peer_addr} connected, receiving {outfile}")
                sock.settimeout(None)        

            if not data:
                continue

            seq = data[0]

            if seq == SEQ_FIN:
                unreliable_sendto(sock, bytes([SEQ_FIN]), peer_addr)
                print("[RECV COMPLETE]", outfile)
                break

            payload = data[1:]

            if seq == expected:
                f.write(payload)
                written += len(payload)
                expected = SEQ_DATA_1 if seq == SEQ_DATA_0 else SEQ_DATA_0
            else:
                print(f"[DUP] seq={seq} ignored")

            unreliable_sendto(sock, bytes([seq]), peer_addr)

    return peer_addr, written


def client_mode(args):
    if not (args.file or args.save):
        print("[FATAL] Specify at least --file to send or --save to receive")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    peer = (args.host, args.port)

    if args.file:
        send_file(sock, peer, args.file, args.timeout)

    if args.save:
        sock.sendto(b'HELLO', peer)
        peer_addr, bytes_written = receive_file(sock, args.save, first_timeout=args.timeout)
        print(f"[STATS] wrote {bytes_written} bytes to {args.save}")

    sock.close()


def server_mode(args):
    if not (args.out or args.send):
        print("[FATAL] Specify at least --out to receive or --send to transmit")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', args.port))
    print(f"[LISTEN] UDP {args.port}")

    peer_addr = None
    if args.out:
        peer_addr, bytes_written = receive_file(sock, args.out, first_timeout=None)
        print(f"[STATS] wrote {bytes_written} bytes to {args.out}")

    if args.send:
        if peer_addr is None:
            try:
                print('[WAIT] HELLO from client')
                sock.settimeout(None)
                _, peer_addr = sock.recvfrom(16)
                sock.settimeout(args.timeout)
            except (socket.timeout, ConnectionResetError):
                print("[ERROR] No client contacted the server – cannot send.")
                sys.exit(1)
        send_file(sock, peer_addr, args.send, args.timeout)

    sock.close()


def main():
    p = argparse.ArgumentParser(description='Bidirectional Stop‑and‑Wait ARQ demo over UDP')
    sub = p.add_subparsers(dest='role', required=True)

    c = sub.add_parser('client', help='run as client (active opener)')
    c.add_argument('host', help='server hostname/IP')
    c.add_argument('port', type=int, help='server UDP port')
    c.add_argument('--file', help='file to send to server')
    c.add_argument('--save', help='filename to store data received from server')
    c.add_argument('-t', '--timeout', type=float, default=TIMEOUT_DEFAULT,
                   help='socket timeout (seconds)')


    s = sub.add_parser('server', help='run as server (passive listener)')
    s.add_argument('port', type=int, help='UDP port to listen on')
    s.add_argument('--out', help='filename to store data received from client')
    s.add_argument('--send', help='file to transmit to client after (or without) receiving')
    s.add_argument('-t', '--timeout', type=float, default=TIMEOUT_DEFAULT,
                   help='socket timeout (seconds)')

    args = p.parse_args()
    random.seed()

    if args.role == 'client':
        client_mode(args)
    else:
        server_mode(args)


if __name__ == '__main__':
    main()
