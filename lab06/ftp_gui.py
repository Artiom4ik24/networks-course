import tkinter as tk
from tkinter import messagebox, simpledialog
from ftplib import FTP
import io

class FTPGUIClient:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP GUI Client")
        self.ftp = None

        self.build_login_ui()

    def build_login_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Хост:").grid(row=0, column=0)
        self.host_entry = tk.Entry(frame)
        self.host_entry.grid(row=0, column=1)
        self.host_entry.insert(0, "127.0.0.1")

        tk.Label(frame, text="Порт:").grid(row=1, column=0)
        self.port_entry = tk.Entry(frame)
        self.port_entry.grid(row=1, column=1)
        self.port_entry.insert(0, "21")

        tk.Label(frame, text="Логин:").grid(row=2, column=0)
        self.user_entry = tk.Entry(frame)
        self.user_entry.grid(row=2, column=1)
        self.user_entry.insert(0, "TestUser")

        tk.Label(frame, text="Пароль:").grid(row=3, column=0)
        self.pass_entry = tk.Entry(frame, show="*")
        self.pass_entry.grid(row=3, column=1)
        self.pass_entry.insert(0, "password")

        tk.Button(frame, text="Подключиться", command=self.connect).grid(row=4, column=0, columnspan=2, pady=5)

    def connect(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        user = self.user_entry.get()
        passwd = self.pass_entry.get()

        try:
            self.ftp = FTP()
            self.ftp.connect(host, port)
            self.ftp.login(user=user, passwd=passwd)
            self.ftp.cwd('shared')
            messagebox.showinfo("Успех", f"Подключено к {host}")
            self.show_main_ui()
        except Exception as e:
            messagebox.showerror("Ошибка подключения", str(e))

    def show_main_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.file_listbox = tk.Listbox(self.root, width=60)
        self.file_listbox.pack(padx=10, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Обновить список", command=self.refresh_list).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Создать файл", command=self.create_file).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Просмотреть", command=self.retrieve_file).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.update_file).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_file).grid(row=0, column=4, padx=5)

        self.text_output = tk.Text(self.root, height=15, width=80)
        self.text_output.pack(padx=10, pady=5)

        self.refresh_list()

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            files = self.ftp.nlst()
            for f in files:
                self.file_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def retrieve_file(self):
        filename = self._get_selected_file()
        if not filename:
            return

        content = io.BytesIO()
        try:
            self.ftp.retrbinary(f"RETR {filename}", content.write)
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, content.getvalue().decode())
        except Exception as e:
            messagebox.showerror("Ошибка чтения", str(e))

    def create_file(self):
        self._edit_file(new_file=True)

    def update_file(self):
        filename = self._get_selected_file()
        if not filename:
            return
        self._edit_file(filename)

    def _edit_file(self, filename=None, new_file=False):
        editor = tk.Toplevel(self.root)
        editor.title("Редактор файла")

        text = tk.Text(editor, height=20, width=70)
        text.pack()

        if filename and not new_file:
            content = io.BytesIO()
            self.ftp.retrbinary(f"RETR {filename}", content.write)
            text.insert(tk.END, content.getvalue().decode())

        def save_file():
            new_content = text.get("1.0", tk.END).encode()
            if new_file:
                filename_to_create = simpledialog.askstring("Создать файл", "Введите имя нового файла:")
                if not filename_to_create:
                    return
                self.ftp.storbinary(f"STOR {filename_to_create}", io.BytesIO(new_content))
                messagebox.showinfo("Готово", f"Файл {filename_to_create} создан.")
            else:
                self.ftp.storbinary(f"STOR {filename}", io.BytesIO(new_content))
                messagebox.showinfo("Готово", f"Файл {filename} обновлён.")

            editor.destroy()
            self.refresh_list()

        tk.Button(editor, text="Сохранить", command=save_file).pack(pady=5)

    def delete_file(self):
        filename = self._get_selected_file()
        if not filename:
            return
        confirm = messagebox.askyesno("Подтвердите удаление", f"Удалить файл {filename}?")
        if confirm:
            try:
                self.ftp.delete(filename)
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Ошибка удаления", str(e))

    def _get_selected_file(self):
        try:
            return self.file_listbox.get(self.file_listbox.curselection())
        except:
            messagebox.showwarning("Внимание", "Выберите файл из списка")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPGUIClient(root)
    root.mainloop()
