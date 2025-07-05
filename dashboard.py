import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
import db
from login import LoginApp

class Dashboard:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id
        master.title("BookLog - Meus Livros")

        self.label = tk.Label(master, text="Livros cadastrados:")
        self.label.pack()

        self.search_entry = tk.Entry(master)
        self.search_entry.pack()
        self.search_button = tk.Button(master, text="Buscar", command=self.search_books)
        self.search_button.pack(pady=2)

        self.listbox = tk.Listbox(master, width=50)
        self.listbox.pack(pady=5)

        self.refresh_books()

        self.add_button = tk.Button(master, text="Adicionar Livro", command=self.add_book)
        self.add_button.pack(pady=2)

        self.edit_button = tk.Button(master, text="Editar Selecionado", command=self.edit_book)
        self.edit_button.pack(pady=2)

        self.remove_button = tk.Button(master, text="Remover Selecionado", command=self.remove_book)
        self.remove_button.pack(pady=2)

        self.stats_button = tk.Button(master, text="Ver Estatísticas", command=self.show_stats)
        self.stats_button.pack(pady=2)

        self.logout_button = tk.Button(master, text="Logout", command=self.handle_logout)
        self.logout_button.pack(pady=10)

    def refresh_books(self, search_query=None):
        self.listbox.delete(0, tk.END)
        conn = db.connect()
        cursor = conn.cursor()
        if search_query:
            cursor.execute("""
                SELECT id, title, author, status FROM books
                WHERE user_id=? AND (title LIKE ? OR author LIKE ?)
            """, (self.user_id, f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT id, title, author, status FROM books WHERE user_id=?", (self.user_id,))
        self.books = cursor.fetchall()
        conn.close()

        for book in self.books:
            text = f"{book[1]} - {book[2]} [{book[3]}]"
            self.listbox.insert(tk.END, text)

    def add_book(self):
        title = simpledialog.askstring("Título", "Digite o título do livro:")
        author = simpledialog.askstring("Autor", "Digite o autor do livro:")
        status = simpledialog.askstring("Status", "Digite o status (lido/não lido):")

        if title:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (user_id, title, author, status) VALUES (?, ?, ?, ?)",
                        (self.user_id, title, author, status))
            conn.commit()
            conn.close()
            self.refresh_books()

    def edit_book(self):
        selection = self.listbox.curselection()
        if not selection:
            return messagebox.showwarning("Aviso", "Selecione um livro para editar")

        index = selection[0]
        book_id, old_title, old_author, old_status = self.books[index]

        new_title = simpledialog.askstring("Editar Título", "Novo título:", initialvalue=old_title)
        new_author = simpledialog.askstring("Editar Autor", "Novo autor:", initialvalue=old_author)
        new_status = simpledialog.askstring("Editar Status", "Novo status:", initialvalue=old_status)

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE books SET title=?, author=?, status=? WHERE id=? AND user_id=?
        """, (new_title, new_author, new_status, book_id, self.user_id))
        conn.commit()
        conn.close()
        self.refresh_books()

    def remove_book(self):
        selection = self.listbox.curselection()
        if not selection:
            return messagebox.showwarning("Aviso", "Selecione um livro para remover")

        index = selection[0]
        book_id = self.books[index][0]

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, self.user_id))
        conn.commit()
        conn.close()
        self.refresh_books()

    def search_books(self):
        query = self.search_entry.get()
        self.refresh_books(search_query=query)

    def show_stats(self):
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM books WHERE user_id=? GROUP BY status", (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("Estatísticas", "Nenhum dado para exibir.")
            return

        labels = [row[0] for row in data]
        counts = [row[1] for row in data]

        plt.figure(figsize=(5, 4))
        plt.bar(labels, counts, color=['green', 'gray'])
        plt.title("Livros por Status")
        plt.ylabel("Quantidade")
        plt.show()

    def handle_logout(self):
        self.master.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()
