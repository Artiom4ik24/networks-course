import random
import sys
from typing import List, Tuple

POLY = 0x1021
INIT = 0xFFFF


def crc16_ccitt(data: bytes, poly: int = POLY, init: int = INIT):
    crc = init
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc


def encode_packet(data: bytes):
    if len(data) != 5:
        raise ValueError("Data payload must be exactly 5 bytes.")
    crc = crc16_ccitt(data)

    return data + crc.to_bytes(2, "big")


def verify_packet(packet: bytes):
    if len(packet) != 7:
        raise ValueError("Packet must be exactly 7 bytes: 5 data + 2 CRC.")
    data, recv_crc = packet[:5], int.from_bytes(packet[5:], "big")
    return data, recv_crc == crc16_ccitt(data)


def inject_errors(packet: bytes, n_errors: int = 1):
    mutable = bytearray(packet)
    total_bits = len(mutable) * 8
    for i in range(max(1, n_errors)):
        bit = random.randrange(total_bits)
        mutable[bit // 8] ^= 1 << (bit % 8)
    return bytes(mutable)


def chunk_data(text: str, size: int = 5) -> List[bytes]:
    raw = text.encode("utf‑8")
    chunks = []
    for i in range(0, len(raw), size):
        chunk = raw[i : i + size]
        if len(chunk) < size:
            chunk = chunk.ljust(size, b"\x00")
        chunks.append(chunk)

    return chunks


def run_self_tests() -> bool:
    print("Running tests...\n")
    all_passed = True

    data = b"ABCDE"
    pkt = encode_packet(data)
    _, ok = verify_packet(pkt)
    if ok:
        print("[PASS] Round‑trip CRC verification")
    else:
        print("[FAIL] Round‑trip CRC verification")
        all_passed = False


    data = b"12345"
    pkt = encode_packet(data)
    corrupted = inject_errors(pkt)
    _, ok = verify_packet(corrupted)
    if not ok:
        print("[PASS] CRC detects single‑bit error")
    else:
        print("[FAIL] CRC detects single‑bit error")
        all_passed = False


    for i in range(1, 5):
        rnd_data = random.randbytes(5)
        pkt = encode_packet(rnd_data)
        corrupted = inject_errors(pkt, random.randint(1, 3))
        _, clean_ok = verify_packet(pkt)
        _, corrupt_ok = verify_packet(corrupted)
        if clean_ok and not corrupt_ok:
            print(f"[PASS] Random packet #{i}")
        else:
            print(f"[FAIL] Random packet #{i}")
            all_passed = False

    print("\nSelf‑tests completed.")
    return all_passed


def demo(text: str, error_packets: List[int]):
    packets = [encode_packet(chunk) for chunk in chunk_data(text)]

    print("Encoded packets (data | CRC | full):")
    for i, p in enumerate(packets):
        print(f"{i:02d}: {p[:5].hex()} | {p[5:].hex()} | {p.hex()}")


    print("\nInjecting artificial errors into packets:", error_packets)
    for i in error_packets:
        if 0 <= i < len(packets):
            packets[i] = inject_errors(packets[i])

    print("\nVerification results:")
    for i, p in enumerate(packets):
        data, ok = verify_packet(p)
        status = "OK" if ok else "ERROR"
        print(f"{i:02d}: {status} | data={data.hex()} | packet={p.hex()}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = run_self_tests()
        sys.exit(0 if success else 1)

    text = input("Введите текст для отправки: ")
    errs = input("Номера пакетов для искажения (через запятую, например 1,3): ")
    indices = [int(x) for x in errs.split(',') if x.strip().isdigit()]
    demo(text, indices)
