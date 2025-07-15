import tkinter as tk
from tkinter import messagebox
import hashlib
import db
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)

    cursor.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def register(username, password):
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        conn.close()

class LoginApp:
    def __init__(self, master):
        self.master = master
        master.title("BookLog - Login")

        self.label1 = tk.Label(master, text="Usuário:")
        self.label1.pack()
        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        self.label2 = tk.Label(master, text="Senha:")
        self.label2.pack()
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(master, text="Login", command=self.handle_login)
        self.login_button.pack(pady=5)

        self.register_button = tk.Button(master, text="Cadastrar", command=self.handle_register)
        self.register_button.pack()

        self.quit_button = tk.Button(master, text="Sair", command=self.handle_quit)
        self.quit_button.pack(pady=10)

    def handle_login(self):
        from dashboard import Dashboard
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = login(username, password)

        if user_id:
            messagebox.showinfo("Login", f"Bem-vindo(a), {username}!")
            self.master.destroy()
            root = tk.Tk()
            Dashboard(root, user_id)
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")


    def handle_register(self):
        register_window = tk.Toplevel(self.master)
        register_window.title("Cadastro de Usuário")
        register_window.geometry("300x200")
        register_window.resizable(False, False)

        frame = tk.Frame(register_window, padx= 20, pady=20)
        frame.pack(expand=True)

        tk.Label(frame, text="Novo Usuário:").pack(anchor='w')
        new_username_entry = tk.Entry(frame, width=30)
        new_username_entry.pack(pady=5)

        tk.Label(frame, text="Senha:").pack(anchor='w')
        new_password_entry = tk.Entry(frame,show="*", width=30)
        new_password_entry.pack(pady=5)

        def concluir_caddastro():
            username = new_username_entry.get()
            password = new_password_entry.get()

            if not username or not password:
                messagebox.showwarning("Campos vazios", "Preencha todos os campos")
                return

            result = register(username, password)
            if result == True:
                messagebox.showinfo("Cadastro", "Usuário cadastrado com sucesso")
                register_window.destroy()
            elif result == "duplicate":
                messagebox.showinfo("Usuário já cadastrado", "Este nome de usuário já está em uso. Escolha outro.")
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao cadastrar o usuário. Tente novamente.")
        tk.Button(register_window, text="Concluir Cadastro", command=concluir_caddastro).pack(pady=10)

    def handle_quit(self):
        self.master.quit()

if __name__ == "__main__":
    db.init_db()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
