import tkinter as tk
from login import LoginApp
import db

if __name__ == "__main__":
    db.init_db()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
