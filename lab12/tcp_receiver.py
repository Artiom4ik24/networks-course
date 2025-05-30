import socket, struct, threading, time, tkinter as tk, tkinter.messagebox as mb

PACKET_SIZE = 1024

class ReceiverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Получатель TCP")
        self.root.resizable(False, False)

        tk.Label(text="Введите IP").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        tk.Label(text="Выберите порт для получения").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        tk.Label(text="Скорость передачи").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        tk.Label(text="Число полученных пакетов").grid(row=3, column=0, sticky="w", padx=8, pady=4)

        self.ip = tk.Entry(width=20); self.ip.insert(0,"0.0.0.0")
        self.port = tk.Entry(width=20); self.port.insert(0,"8080")
        self.speed = tk.Entry(width=20); self.packets = tk.Entry(width=20)
        for e in (self.speed, self.packets): e.configure(state="readonly")

        self.ip.grid(row=0,column=1, pady=4); self.port.grid(row=1,column=1, pady=4)
        self.speed.grid(row=2,column=1, pady=4); self.packets.grid(row=3,column=1, pady=4)

        self.btn = tk.Button(text="Получить", width=15, command=self.start_server)
        self.btn.grid(row=4, column=0, columnspan=2, pady=12)
        self.root.mainloop()

    def start_server(self):
        try:
            ip = self.ip.get().strip()
            port = int(self.port.get().strip())
        except ValueError:
            mb.showerror("Ошибка", "Неверный порт")
            return
        self.btn.config(state="disabled")
        threading.Thread(target=self.run_server, args=(ip, port), daemon=True).start()

    def update_field(self, entry, text):
        entry.config(state="normal"); entry.delete(0,"end"); entry.insert(0, text); entry.config(state="readonly")

    def run_server(self, ip, port):
        try:
            srv = socket.socket(); srv.bind((ip, port)); srv.listen(1)
            conn, addr = srv.accept()

            hdr = conn.recv(4); 
            if len(hdr) < 4: raise ConnectionError("Клиент закрыл соединение :(")
            packets_expected = struct.unpack("!I", hdr)[0]

            received = 0; start = time.perf_counter()
            while received < packets_expected:
                chunk = conn.recv(PACKET_SIZE)
                if not chunk: break
                received += 1
            end = time.perf_counter()
            conn.close(); srv.close()

            duration = max(0.0001, end - start)
            speed_bps = (received * PACKET_SIZE) / duration
            self.update_field(self.speed, f"{speed_bps:,.0f} B/s")
            self.update_field(self.packets, f"{received} of {packets_expected}")
        except Exception as e:
            mb.showerror("Ошибка", str(e))
        finally:
            self.btn.config(state="normal")

if __name__ == "__main__":
    ReceiverGUI()
