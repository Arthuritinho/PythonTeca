import sqlite3

def connect():
    conn = sqlite3.connect("pythonteca.db")
    conn.execute("PRAGMA foreign_keys = ON")  # ✅ Garante integridade referencial
    return conn


def init_db():
    conn = connect()
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            cpf TEXT PRIMARY KEY,              -- CPF será o ID único do usuário
            username TEXT NOT NULL,            -- Nome do usuário
            email TEXT,                        -- E-mail (opcional)
            password_hash TEXT NOT NULL        -- Senha criptografada (SHA-256)
        )
    """)

    # Tabela de livros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,             -- CPF do usuário dono do livro
            title TEXT NOT NULL,               -- Título do livro
            author TEXT NOT NULL,              -- Autor
            status TEXT NOT NULL,              -- Status: "desejado", "em leitura", "lido"
            total_pages INTEGER DEFAULT 0,     -- Total de páginas do livro
            pages_read INTEGER DEFAULT 0,      -- Quantas páginas já foram lidas
            notes TEXT,                        -- Anotações opcionais
            FOREIGN KEY(user_id) REFERENCES users(cpf) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ======== FUNÇÕES DE USUÁRIOS ========
def add_user(cpf, username, email, password_hash):
    # Adiciona um novo usuário ao banco.
    # Retorna True se o cadastro foi bem-sucedido ou False se o CPF já existe.
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (cpf, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (cpf, username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(cpf, password_hash):
    # Busca usuário pelo CPF e senha.
    # Retorna o CPF se encontrado, ou None se não houver correspondência.
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cpf FROM users WHERE cpf=? AND password_hash=?
    """, (cpf, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def user_exists(cpf):
    # Verifica se um usuário com determinado CPF já existe no banco.
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT cpf FROM users WHERE cpf=?", (cpf,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ======== FUNÇÃO DE DEBUG (opcional) ========
def show_all():
    # Mostra todos os usuários e livros do banco (para debug).
    conn = connect()
    cursor = conn.cursor()

    print("\n📋 Usuários cadastrados:")
    for row in cursor.execute("SELECT * FROM users"):
        print(row)

    print("\n📚 Livros cadastrados:")
    for row in cursor.execute("SELECT * FROM books"):
        print(row)

    conn.close()


# ======== EXECUÇÃO DIRETA ========
if __name__ == "__main__":
    init_db()
    print("✅ Banco de dados inicializado!")
    show_all()
