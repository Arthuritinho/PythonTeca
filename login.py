import tkinter as tk
from tkinter import messagebox
import hashlib
import db
import sqlite3

# ----------------- HASH DA SENHA -----------------
def hash_password(password):
    # Criptografa a senha usando SHA-256.
    return hashlib.sha256(password.encode()).hexdigest()


# ----------------- LOGIN -----------------
def login(cpf, password):
    # Verifica se o CPF e a senha estão corretos no banco.
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)

    cursor.execute("SELECT cpf FROM users WHERE cpf=? AND password_hash=?", (cpf, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# ----------------- CADASTRO -----------------
def register(cpf, username, password, email=None):
    # Cadastra novo usuário.
    # CPF é único (PRIMARY KEY). Caso já exista, retorna 'duplicate'.
    conn = db.connect()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (cpf, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (cpf, username, email, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return "duplicate"
    except Exception:
        conn.close()
        return False


# ----------------- JANELA DE CADASTRO -----------------
class RegisterWindow:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Cadastrar Usuário")

        # CPF
        tk.Label(self.top, text="CPF:").pack()
        self.cpf_entry = tk.Entry(self.top)
        self.cpf_entry.pack()

        # Nome de usuário
        tk.Label(self.top, text="Usuário:").pack()
        self.username_entry = tk.Entry(self.top)
        self.username_entry.pack()

        # Senha
        tk.Label(self.top, text="Senha:").pack()
        self.password_entry = tk.Entry(self.top, show="*")
        self.password_entry.pack()

        # Email opcional
        tk.Label(self.top, text="E-mail (opcional):").pack()
        self.email_entry = tk.Entry(self.top)
        self.email_entry.pack()

        # Botão de cadastro
        self.submit_button = tk.Button(self.top, text="Concluir", command=self.submit)
        self.submit_button.pack(pady=5)

    def submit(self):
        # Tenta cadastrar o usuário e trata mensagens.
        cpf = self.cpf_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        email = self.email_entry.get().strip() or None

        # ✅ Validação básica
        if not cpf or not username or not password:
            messagebox.showwarning("Atenção", "CPF, usuário e senha são obrigatórios.")
            return

        result = register(cpf, username, password, email)
        if result == True:
            messagebox.showinfo("Cadastro", "✅ Usuário cadastrado com sucesso!")
            self.top.destroy()
        elif result == "duplicate":
            messagebox.showerror("Erro", "❌ Este CPF já está cadastrado.")
        else:
            messagebox.showerror("Erro", "⚠ Ocorreu um problema ao cadastrar o usuário.")


# ----------------- JANELA DE LOGIN -----------------
class LoginApp:
    def __init__(self, master):
        self.master = master
        master.title("BookLog - Login")

        # CPF
        tk.Label(master, text="CPF:").pack()
        self.cpf_entry = tk.Entry(master)
        self.cpf_entry.pack()

        # Senha
        tk.Label(master, text="Senha:").pack()
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        # Botões
        self.login_button = tk.Button(master, text="Login", command=self.handle_login)
        self.login_button.pack(pady=5)

        self.register_button = tk.Button(master, text="Cadastrar Usuário", command=self.open_register_window)
        self.register_button.pack()

        self.quit_button = tk.Button(master, text="Sair", command=self.handle_quit)
        self.quit_button.pack(pady=10)

    def handle_login(self):
        # Tenta logar o usuário pelo CPF.
        from dashboard import Dashboard
        cpf = self.cpf_entry.get().strip()
        password = self.password_entry.get()
        user_cpf = login(cpf, password)

        if user_cpf:
            messagebox.showinfo("Login", f"✅ Bem-vindo!")
            self.master.destroy()
            root = tk.Tk()
            Dashboard(root, user_cpf)
            root.mainloop()
        else:
            messagebox.showerror("Erro", "❌ CPF ou senha inválidos.")

    def open_register_window(self):
        # Abre a janela de cadastro de usuário.
        RegisterWindow(self.master)

    def handle_quit(self):
        self.master.quit()


# ----------------- INICIALIZAÇÃO -----------------
if __name__ == "__main__":
    db.init_db()  # Cria o banco de dados e tabelas, se não existirem
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
