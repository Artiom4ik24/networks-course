import subprocess
import re

if __name__ == "__main__":
    output = subprocess.check_output("ipconfig", encoding='cp866')
    ip_pattern = re.compile(r"IPv4-адрес.*?:\s*([\d.]+)")
    mask_pattern = re.compile(r"Маска подсети.*?:\s*([\d.]+)")

    ip_addresses = ip_pattern.findall(output)
    subnet_masks = mask_pattern.findall(output)

    for ip, mask in zip(ip_addresses, subnet_masks):
        print(f"IP-адрес: {ip}")
        print(f"Маска сети: {mask}")
        print()

