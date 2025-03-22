#!/usr/bin/env python3
import socket
import sys
import base64
import os

def get_password_from_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()

def send_command(sock, command):
    cmd_str = command + "\r\n"
    print(f">>> {command}")
    sock.sendall(cmd_str.encode("utf-8"))
    
    response = sock.recv(1024).decode("utf-8", errors="replace")
    print(f"<<< {response.strip()}")
    return response

def main():
    to_email ="artiom4ik24@yandex.ru"
    subject="I am a cat"
    body=body = (
        "Hello, I would like you to know that I am just a cat."
    )
    from_email ="no_reply@bechair.online"
    smtp_server="smtp.spaceweb.ru"
    smtp_port=2525
    password_file="password.txt"
    
    password = get_password_from_file(password_file)
    if not password:
        print("Ошибка: не удалось прочитать пароль из файла.")
        sys.exit(1)

    image_path = "cat.jpg" 
    image_filename = os.path.basename(image_path)

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"Файл {image_path} не найден.")
        sys.exit(1)
        
    image_b64 = None
    if image_data:
        image_b64 = base64.b64encode(image_data).decode("ascii")


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((smtp_server, smtp_port))

        banner = sock.recv(1024).decode("utf-8", errors="replace")
        print("<<<", banner.strip())

        send_command(sock, f"HELO {from_email.split('@')[1]}")

        send_command(sock, "AUTH LOGIN")

        encoded_username = base64.b64encode(from_email.encode("utf-8")).decode("ascii")
        response = send_command(sock, encoded_username)

        encoded_password = base64.b64encode(password.encode("utf-8")).decode("ascii")
        response = send_command(sock, encoded_password)

        send_command(sock, f"MAIL FROM:<{from_email}>")

        send_command(sock, f"RCPT TO:<{to_email}>")

        send_command(sock, "DATA")

        boundary = "BOUNDARY1234567890"

        data_lines = []
        data_lines.append(f"From: {from_email}")
        data_lines.append(f"To: {to_email}")
        data_lines.append(f"Subject: {subject}")
        data_lines.append("MIME-Version: 1.0")
        data_lines.append(f"Content-Type: multipart/mixed; boundary=\"{boundary}\"")
        data_lines.append("")

        data_lines.append(f"--{boundary}")
        data_lines.append("Content-Type: text/plain; charset=\"utf-8\"")
        data_lines.append("Content-Transfer-Encoding: 7bit")
        data_lines.append("")
        data_lines.append(body) 

        data_lines.append(f"--{boundary}")
        data_lines.append(f"Content-Type: image/jpg; name=\"{image_filename}\"")
        data_lines.append("Content-Transfer-Encoding: base64")
        data_lines.append(f"Content-Disposition: attachment; filename=\"{image_filename}\"")
        data_lines.append("")
        data_lines.append(image_b64)

        data_lines.append(f"--{boundary}--")
        data_lines.append(".")

        data_message = "\r\n".join(data_lines) + "\r\n"

        print(">>> sending DATA content ...")
        sock.sendall(data_message.encode("utf-8"))

        response = sock.recv(1024).decode("utf-8", errors="replace")
        print(f"<<< {response.strip()}")

        send_command(sock, "QUIT")

if __name__ == "__main__":
    main()
