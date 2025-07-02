import tkinter as tk
from tkinter import messagebox
import hashlib
import db
import dashboard

# Gerar o hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verificar o login
def login(username, password):
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)

    cursor.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Retorna o ID do usuário
    return None

# Cadastrar um novo usuário
def register(username, password):
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Interface gráfica de login
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

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = login(username, password)

        if user_id:
            messagebox.showinfo("Login", f"Bem-vindo, {username}!")
            self.master.destroy()
            root = tk.Tk()
            app = dashboard.Dashboard(root, user_id)
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    def handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if register(username, password):
            messagebox.showinfo("Cadastro", "Usuário cadastrado com sucesso")
        else:
            messagebox.showerror("Erro", "Usuário já existe")

if __name__ == "__main__":
    db.init_db()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
