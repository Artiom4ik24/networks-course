import socket, struct, threading, tkinter as tk, tkinter.messagebox as mb

PACKET_SIZE = 1024

class SenderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Отправитель TCP")
        self.root.resizable(False, False)

        tk.Label(text="Введите IP адрес получателя").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        tk.Label(text="Выберите порт отправки").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        tk.Label(text="Введите количество пакетов для отправки").grid(row=2, column=0, sticky="w", padx=8, pady=4)

        self.ip = tk.Entry(width=20); self.ip.insert(0, "127.0.0.1")
        self.port = tk.Entry(width=20); self.port.insert(0, "8080")
        self.num = tk.Entry(width=20); self.num.insert(0, "5")
        self.ip.grid(row=0,column=1, pady=4); self.port.grid(row=1,column=1, pady=4); self.num.grid(row=2,column=1, pady=4)

        self.btn = tk.Button(text="Отправить", width=15, command=self.start_send)
        self.btn.grid(row=3, column=0, columnspan=2, pady=12)
        self.root.mainloop()

    def start_send(self):
        try:
            ip = self.ip.get().strip()
            port = int(self.port.get().strip())
            num  = int(self.num.get().strip())
            if num <= 0: raise ValueError
        except ValueError:
            mb.showerror("Ошибка", "Проверьте введённые данные")
            return
        self.btn.config(state="disabled")
        threading.Thread(target=self.send_packets, args=(ip,port,num), daemon=True).start()

    def send_packets(self, ip, port, num):
        try:
            sock = socket.create_connection((ip, port), timeout=3)
            sock.sendall(struct.pack("!I", num))
            payload = b"x" * PACKET_SIZE
            for _ in range(num):
                sock.sendall(payload)
            sock.close()
            mb.showinfo("Успех", f"Отправлено {num} пакетов по {PACKET_SIZE} B")
        except Exception as e:
            mb.showerror("Ошибка", f"Не удалось отправить данные:\n{e}")
        finally:
            self.btn.config(state="normal")

if __name__ == "__main__":
    SenderGUI()
