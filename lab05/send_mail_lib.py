#!/usr/bin/env python3

import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_password_from_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def send_email(
    to_address: str,
    subject: str,
    body: str,
    from_address: str = "sender@example.com",
    smtp_server: str = "smtp.example.com",
    smtp_port: int = 587,
    login: str = "sender@example.com",
    password_file: str = "password.txt",
    is_html: bool = True
):
    
    password = get_password_from_file(password_file)
    if not password:
        print("Ошибка: не удалось прочитать пароль из файла.")
        sys.exit(1)

    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject

    if is_html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.login(login, password)
            server.sendmail(from_address, to_address, msg.as_string())

        print(f"Письмо успешно отправлено на {to_address}")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


def main():
    if len(sys.argv) < 2:
        print("Пример использования:\n"
              "  python send_mail_lib.py <to_address>")
        sys.exit(1)

    to_address = sys.argv[1]
    format_type = 'html'
    subject = "This is a test of automatic email sending."

    body = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width" />
  <title>Automatic Email Sending Test</title>
</head>
<body style="margin:0; padding:0; font-family:Arial, sans-serif;">

  <!-- Main container -->
  <div style="max-width:600px; margin:0 auto; border:1px solid #ddd;">
    
    <div style="padding:20px; border-bottom:1px solid #ddd;">
      <h1 style="margin:0; font-size:24px;">
        Automatic Email Sending Test
      </h1>
      <p style="margin:5px 0 0 0; font-size:14px; color:#555;">
        This email was generated automatically
      </p>
    </div>
    
    <div style="padding:20px;">
      <p style="font-size:16px; line-height:1.5; margin:0 0 15px 0; color:#333;">
        Hello,
      </p>
      <p style="font-size:16px; line-height:1.5; margin:0 0 15px 0; color:#333;">
        This email serves as a test to verify automatic email sending functionality. 
        Please disregard if you received it by mistake.
      </p>
      <p style="font-size:16px; line-height:1.5; margin:0 0 15px 0; color:#333;">
        Thank you for your time!
      </p>
    </div>
    
    <div style="padding:20px; border-top:1px solid #ddd; text-align:center;">
      <p style="font-size:12px; color:#999; margin:0;">
        &copy; 2025 Your Company Name. All rights reserved.<br />
        MCS faculty, SPBU, Saint Petersburg, Russia
      </p>
    </div>

  </div>
</body>
</html>
"""
    is_html = (format_type == "html")

    send_email(
        to_address=to_address,
        subject=subject,
        body=body,
        from_address="no_reply@bechair.online",
        smtp_server="smtp.spaceweb.ru",
        smtp_port=2525,
        login="no_reply@bechair.online",
        password_file="password.txt",
        is_html=is_html
    )


if __name__ == "__main__":
    main()
