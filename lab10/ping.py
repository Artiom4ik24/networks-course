import os, sys, time, struct, socket, statistics, argparse, select

def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b'\x00'
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

def build_packet(ident: int, seq: int) -> bytes:
    header = struct.pack("!BBHHH", 8, 0, 0, ident, seq)
    payload = struct.pack("!d", time.time())
    chksum  = checksum(header + payload)
    header  = struct.pack("!BBHHH", 8, 0, chksum, ident, seq)
    return header + payload

def ping(dest_addr: str, count=4):
    try:
        dest_ip = socket.gethostbyname(dest_addr)
    except socket.gaierror as e:
        sys.exit(f"Cannot resolve {dest_addr}: {e}")

    print(f"PING {dest_addr} ({dest_ip}) {8+8} bytes of data:")

    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    ident = os.getpid() & 0xffff
    seq = 0
    rtts = []
    sent = recv = 0

    while seq < count:
        seq += 1
        pkt = build_packet(ident, seq)
        sent += 1
        send_time = time.time()
        sock.sendto(pkt, (dest_ip, 0))

        # ждём ответа не дольше 1 секунды
        started_select = time.time()
        ready = select.select([sock], [], [], 1)
        waited = time.time() - started_select
        if ready[0]:
            recv_time, rtt_ms = receive_reply(sock, ident, seq)
            if rtt_ms is not None:
                recv += 1
                rtts.append(rtt_ms)
                print(f"{len(pkt)} bytes from {dest_ip}: icmp_seq={seq} ttl={recv_time}")
                print(f"RTT min: {min(rtts):.3f} max: {max(rtts):.3f} avg: {statistics.mean(rtts):.3f} ms")

        else:
            print(f"Request timeout for icmp_seq {seq}")

        # соблюдаем 1-секундный интервал между отправками
        time.sleep(max(0, 1 - waited))

    loss = (sent - recv) / sent * 100
    print(f"\n--- {dest_addr} ping statistics ---")
    print(f"{sent} packets transmitted, {recv} received, {loss:.0f}% packet loss")
    if rtts:
        print("round-trip min/avg/max/stddev = "
              f"{min(rtts):.3f}/{statistics.mean(rtts):.3f}/"
              f"{max(rtts):.3f}/{statistics.pstdev(rtts):.3f} ms")

def receive_reply(sock, ident, seq):
    packet, addr = sock.recvfrom(1024)
    ip_header = packet[:20]
    ip_ttl    = ip_header[8]
    icmp_header = packet[20:28]
    type, code,_csum, r_id, r_seq = struct.unpack("!BBHHH", icmp_header)
    if type == 0 and r_id == ident and r_seq == seq:
        payload = packet[28:36]
        send_ts, = struct.unpack("!d", payload)
        rtt_ms = (time.time() - send_ts) * 1000
        return ip_ttl, rtt_ms
    
    return ip_ttl, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Name or IP address of the host")
    parser.add_argument("-c", "--count", type=int, default=4,
                        help="Number of requests to send (default: 4)")
    args = parser.parse_args()
    try:
        ping(args.host, args.count)
    except KeyboardInterrupt:
        print("\nPing interrupted.")
