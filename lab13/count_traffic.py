#!/usr/bin/env python3
# traffic_monitor.py

import psutil
import time
import tkinter as tk

class TrafficMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Сетевой трафик")
        self.root.geometry("300x150")
        self.root.resizable(False, False)

        self.label_in  = tk.Label(text="Входящий: 0 B", font=("Arial", 12))
        self.label_out = tk.Label(text="Исходящий: 0 B", font=("Arial", 12))
        self.label_rate = tk.Label(text="Скорость: 0 B/s", font=("Arial", 10), fg="gray")

        self.label_in.pack(pady=10)
        self.label_out.pack()
        self.label_rate.pack(pady=10)

        self.last_recv = 0
        self.last_sent = 0
        self.update()
        self.root.mainloop()

    def update(self):
        counters = psutil.net_io_counters()
        recv = counters.bytes_recv
        sent = counters.bytes_sent

        if self.last_recv and self.last_sent:
            delta_recv = recv - self.last_recv
            delta_sent = sent - self.last_sent
            self.label_rate.config(text=f"Скорость: {delta_recv+delta_sent:.0f} B/s")
        self.label_in.config(text=f"Входящий: {recv:,} B")
        self.label_out.config(text=f"Исходящий: {sent:,} B")

        self.last_recv = recv
        self.last_sent = sent
        self.root.after(1000, self.update)  # обновление каждую секунду

if __name__ == "__main__":
    TrafficMonitor()
