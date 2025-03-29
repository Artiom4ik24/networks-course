import socket
import os

FTP_PORT = 21
BUFFER_SIZE = 4096
ENCODING = 'utf-8'

class FTPClient:
    def __init__(self, host, username='TestUser', password='password'):
        self.host = host
        self.username = username
        self.password = password
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.control_socket.connect((self.host, FTP_PORT))
        self._read_response()

        self._send_cmd(f"USER {self.username}")
        self._read_response()

        self._send_cmd(f"PASS {self.password}")
        self._read_response()

        self._send_cmd("CWD shared")
        self._read_response()

    def _send_cmd(self, cmd):
        self.control_socket.send((cmd + '\r\n').encode(ENCODING))

    def _read_response(self):
        resp = self.control_socket.recv(BUFFER_SIZE).decode(ENCODING)
        print(resp)
        return resp

    def _enter_passive_mode(self):
        self._send_cmd("PASV")
        resp = self._read_response()
        start = resp.find('(') + 1
        end = resp.find(')')
        pasv_data = resp[start:end].split(',')
        ip = '.'.join(pasv_data[:4])
        port = (int(pasv_data[4]) << 8) + int(pasv_data[5])
        return ip, port

    def list_files(self):
        ip, port = self._enter_passive_mode()
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((ip, port))

        self._send_cmd("LIST")
        self._read_response()

        data = data_socket.recv(BUFFER_SIZE).decode(ENCODING)
        print("Список файлов/папок:\n", data)

        data_socket.close()
        self._read_response()

    def download_file(self, filename, local_filename=None):
        if not local_filename:
            local_filename = filename

        ip, port = self._enter_passive_mode()
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((ip, port))

        self._send_cmd(f"RETR {filename}")
        self._read_response()

        with open(local_filename, 'wb') as f:
            while True:
                data = data_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)

        data_socket.close()
        self._read_response()
        print(f"Файл {filename} скачан как {local_filename}")

    def upload_file(self, local_filename, remote_filename=None):
        if not remote_filename:
            remote_filename = os.path.basename(local_filename)

        ip, port = self._enter_passive_mode()
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((ip, port))

        self._send_cmd(f"STOR {remote_filename}")
        self._read_response()

        with open(local_filename, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                data_socket.send(data)

        data_socket.close()
        self._read_response()
        print(f"Файл {local_filename} загружен как {remote_filename}")

    def close(self):
        self._send_cmd("QUIT")
        self._read_response()
        self.control_socket.close()

def main():
    host = "127.0.0.1"
    username = "TestUser"
    password = "password"

    ftp = FTPClient(host, username, password)
    ftp.connect()

    while True:
        print("\nДоступные команды:")
        print("1 - Список файлов")
        print("2 - Скачать файл")
        print("3 - Загрузить файл")
        print("4 - Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            ftp.list_files()
        elif choice == '2':
            fname = input("Имя файла на сервере: ")
            local = input("Имя локального файла (Enter — использовать то же имя): ")
            ftp.download_file(fname, local or None)
        elif choice == '3':
            local = input("Путь к локальному файлу: ")
            remote = input("Имя файла на сервере (Enter — использовать то же имя): ")
            ftp.upload_file(local, remote or None)
        elif choice == '4':
            ftp.close()
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
