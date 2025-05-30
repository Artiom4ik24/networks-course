import socket, threading, json, argparse, queue, tkinter as tk, time, sys

MSG_TERM = b"\n"
WIDTH, HEIGHT = 700, 500

def send_json(sock: socket.socket, obj):
    data = json.dumps(obj).encode() + MSG_TERM
    sock.sendall(data)

def recv_json(sock: socket.socket):
    buf = b""
    while MSG_TERM not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError
        buf += chunk
    line, _, remainder = buf.partition(MSG_TERM)
    return json.loads(line), remainder


class ServerApp:
    def __init__(self, host, port):
        self.q = queue.Queue()
        self.root = tk.Tk(); self.root.title("Remote Canvas - SERVER")
        self.cvs  = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="white")
        self.cvs.pack()
        threading.Thread(target=self.net_thread, args=(host, port), daemon=True).start()
        self.poll_queue()
        self.root.mainloop()

    def net_thread(self, host, port):
        srv = socket.socket(); srv.bind((host, port)); srv.listen(1)
        print(f"[SERVER] Ожидание клиента на {host}:{port}…")
        conn, addr = srv.accept()
        print(f"[SERVER] Клиент {addr} подключён")
        try:
            while True:
                obj, _ = recv_json(conn)
                if obj["cmd"] == "line":
                    self.q.put(obj)
        except ConnectionError:
            print("[SERVER] Клиент отключился")

    def poll_queue(self):
        try:
            while True:
                obj = self.q.get_nowait()
                if obj["cmd"] == "line":
                    x1,y1,x2,y2,color = obj["x1"],obj["y1"],obj["x2"],obj["y2"],obj["color"]
                    self.cvs.create_line(x1,y1,x2,y2, fill=color, width=2, capstyle=tk.ROUND)
        except queue.Empty:
            pass
        self.root.after(20, self.poll_queue)


class ClientApp:
    def __init__(self, host, port):
        self.sock = socket.socket(); self.sock.connect((host, port))
        self.root = tk.Tk(); self.root.title("Remote Canvas - CLIENT")
        self.cvs  = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="white")
        self.cvs.pack()
        self.prev = None
        self.color = "black"
        self.cvs.bind("<Button-1>",  self.on_down)
        self.cvs.bind("<B1-Motion>", self.on_move)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_down(self, ev):
        self.prev = (ev.x, ev.y)

    def on_move(self, ev):
        if not self.prev: return
        x1, y1 = self.prev
        x2, y2 = ev.x, ev.y
        self.cvs.create_line(x1,y1,x2,y2, fill=self.color, width=2, capstyle=tk.ROUND)
        send_json(self.sock, {"cmd":"line","x1":x1,"y1":y1,"x2":x2,"y2":y2,"color":self.color})
        self.prev = (x2, y2)
    
    def on_close(self):
        try: self.sock.close()
        except: pass
        self.root.destroy()

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Simple remote drawing over TCP")
    sub = p.add_subparsers(dest="mode", required=True)

    s = sub.add_parser("server", help="run in server mode")
    s.add_argument("host"); s.add_argument("port", type=int)

    c = sub.add_parser("client", help="run in client mode")
    c.add_argument("host")
    c.add_argument("port", type=int)

    args = p.parse_args()

    if args.mode == "server":
        ServerApp(args.host, args.port)
    else:
        ClientApp(args.host, args.port)
