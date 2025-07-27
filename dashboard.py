import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
import db

class Dashboard:
    def __init__(self, master, user_cpf):
        self.master = master
        self.user_cpf = user_cpf  # CPF é o identificador único do usuário
        master.title("PythonTeca - Meus Livros")

        self.label = tk.Label(master, text="📚 Livros cadastrados:")
        self.label.pack()

        self.search_entry = tk.Entry(master)
        self.search_entry.pack()
        self.search_button = tk.Button(master, text="🔍 Buscar", command=self.search_books)
        self.search_button.pack(pady=2)

        self.listbox = tk.Listbox(master, width=80)
        self.listbox.pack(pady=5)

        self.refresh_books()

        # Botões principais
        self.add_button = tk.Button(master, text="➕ Adicionar Livro", command=self.add_book)
        self.add_button.pack(pady=2)

        self.edit_button = tk.Button(master, text="✏️ Editar Selecionado", command=self.edit_book)
        self.edit_button.pack(pady=2)

        self.remove_button = tk.Button(master, text="🗑️ Remover Selecionado", command=self.remove_book)
        self.remove_button.pack(pady=2)

        self.stats_button = tk.Button(master, text="📊 Ver Estatísticas", command=self.show_stats)
        self.stats_button.pack(pady=2)

        self.logout_button = tk.Button(master, text="🚪 Logout", command=self.handle_logout)
        self.logout_button.pack(pady=10)

    def refresh_books(self, search_query=None):
        # Atualiza a lista de livros exibidos
        self.listbox.delete(0, tk.END)
        conn = db.connect()
        cursor = conn.cursor()

        if search_query:
            cursor.execute("""
                SELECT id, title, author, status, total_pages, pages_read, notes
                FROM books
                WHERE user_id=? AND (title LIKE ? OR author LIKE ?)
            """, (self.user_cpf, f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("""
                SELECT id, title, author, status, total_pages, pages_read, notes
                FROM books
                WHERE user_id=?
            """, (self.user_cpf,))
        self.books = cursor.fetchall()
        conn.close()

        for book in self.books:
            progress = self.calculate_progress(book[4], book[5])
            text = f"{book[1]} - {book[2]} [{book[3]}] - {progress}% lido"
            self.listbox.insert(tk.END, text)

    def calculate_progress(self, total_pages, pages_read):
        # Calcula a porcentagem lida
        if not total_pages or total_pages == 0:
            return 0
        return round((pages_read / total_pages) * 100)

    def add_book(self):
        # Adiciona um novo livro ao banco
        title = simpledialog.askstring("Título", "Digite o título do livro:")
        if title is None:
            return

        author = simpledialog.askstring("Autor", "Digite o autor do livro:")
        if author is None:
            return

        status = simpledialog.askstring("Status", "Digite o status (desejado, em leitura, lido):")
        if status is None:
            return

        total_pages = simpledialog.askinteger("Total de Páginas", "Digite o número total de páginas:")
        if total_pages is None:
            return

        pages_read = simpledialog.askinteger("Páginas Lidas", "Digite quantas páginas foram lidas:")
        if pages_read is None:
            return

        notes = simpledialog.askstring("Anotações", "Adicione alguma anotação (opcional):")
        if notes is None:
            notes = ""

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (user_id, title, author, status, total_pages, pages_read, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.user_cpf, title, author, status, total_pages, pages_read, notes))
        conn.commit()
        conn.close()
        self.refresh_books()

    def edit_book(self):
        # Edita um livro selecionado
        selection = self.listbox.curselection()
        if not selection:
            return messagebox.showwarning("Aviso", "Selecione um livro para editar")

        index = selection[0]
        book = self.books[index]
        book_id, old_title, old_author, old_status, old_total, old_read, old_notes = book

        # Perguntas de edição
        new_title = simpledialog.askstring("Editar Título", "Novo título:", initialvalue=old_title)
        if new_title is None:
            return

        new_author = simpledialog.askstring("Editar Autor", "Novo autor:", initialvalue=old_author)
        if new_author is None:
            return

        new_status = simpledialog.askstring("Editar Status", "Novo status:", initialvalue=old_status)
        if new_status is None:
            return

        new_total = simpledialog.askinteger("Editar Total de Páginas", "Novo total de páginas:", initialvalue=old_total)
        if new_total is None:
            return

        new_read = simpledialog.askinteger("Editar Páginas Lidas", "Novo total lido:", initialvalue=old_read)
        if new_read is None:
            return

        new_notes = simpledialog.askstring("Editar Anotações", "Nova anotação:", initialvalue=old_notes)
        if new_notes is None:
            return

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE books 
            SET title=?, author=?, status=?, total_pages=?, pages_read=?, notes=?
            WHERE id=? AND user_id=?
        """, (new_title, new_author, new_status, new_total, new_read, new_notes, book_id, self.user_cpf))
        conn.commit()
        conn.close()
        self.refresh_books()

    def remove_book(self):
        # Remove um livro do banco
        selection = self.listbox.curselection()
        if not selection:
            return messagebox.showwarning("Aviso", "Selecione um livro para remover")

        index = selection[0]
        book_id = self.books[index][0]

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, self.user_cpf))
        conn.commit()
        conn.close()
        self.refresh_books()

    def search_books(self):
        # Busca livros pelo título ou autor
        query = self.search_entry.get()
        self.refresh_books(search_query=query)

    def show_stats(self):
        # Exibe estatísticas de leitura em gráfico de barras
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM books WHERE user_id=? GROUP BY status", (self.user_cpf,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Estatísticas", "Nenhum dado para exibir.")
            return

        labels = [row[0] for row in data]
        counts = [row[1] for row in data]

        plt.figure(figsize=(5, 4))
        plt.bar(labels, counts, color=['green', 'gray', 'blue'])
        plt.title("📊 Livros por Status")
        plt.ylabel("Quantidade")
        plt.show()

    def handle_logout(self):
        # Sai para a tela de login
        from login import LoginApp
        self.master.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()
