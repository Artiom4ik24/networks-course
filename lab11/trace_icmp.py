import socket
import struct
import time
import sys

MAX_HOPS = 30
ATTEMPTS = 3
TIMEOUT = 2.0


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b'\x00'

    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def build_packet(identifier: int, sequence_number: int) -> bytes:
    header = struct.pack("!BBHHH", 8, 0, 0, identifier, sequence_number)
    payload = struct.pack("!d", time.time())
    chk = checksum(header + payload)
    header = struct.pack("!BBHHH", 8, 0, chk, identifier, sequence_number)
    
    return header + payload


def trace(host: str):
    dest_addr = socket.gethostbyname(host)
    print(f"Tracing route to {host} [{dest_addr}] with a maximum of {MAX_HOPS} hops:\n")

    port = 33434
    pid = os.getpid() & 0xFFFF

    for ttl in range(1, MAX_HOPS + 1):
        print(f"{ttl:2}", end=' ')
        for i in range(ATTEMPTS):
            try:
                recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                recv_socket.settimeout(TIMEOUT)

                send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

                recv_socket.bind(("", port))

                packet = build_packet(pid, i)
                send_time = time.time()
                send_socket.sendto(packet, (dest_addr, 0))

                try:
                    data, addr = recv_socket.recvfrom(512)
                    recv_time = time.time()
                    rtt = (recv_time - send_time) * 1000
                    ip = addr[0]

                    icmp_header = data[20:28]
                    icmp_type, code, checksum_val, p_id, sequence = struct.unpack("!BBHHH", icmp_header)

                    print(f"{ip}  {rtt:.2f} ms", end='  ')
                    if icmp_type == 0:
                        print("\nTrace complete.")
                        return
                except socket.timeout:
                    print("*")
            finally:
                send_socket.close()
                recv_socket.close()
        print()


if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser(description="ICMP traceroute")
    parser.add_argument("host", help="Hostname or IP address")
    args = parser.parse_args()

    trace(args.host)
