import sqlite3
import getpass
import tkinter as tk
from tkinter import simpledialog, messagebox

DB_FILE = r"a:\Daily Reports\Negative Balance\App\TheVault.db"

def create_connection():
    try:
        conn = sqlite3.connect(r"a:\Daily Reports\Negative Balance\App\TheVault.db")
        return conn
    except sqlite3.Error as e:
        print(e)
    return None

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                          (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def add_password(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def delete_password(conn, username):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE username = ?", (username,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def get_master_key():
    return getpass.getpass("Enter your master key: ")

class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Custom Dialog")
        tk.Label(master, text="Enter the username:").grid(row=0)
        tk.Label(master, text="Enter the password:").grid(row=1)
        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master, show="*")
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1  # Initial focus set to the username entry

    def apply(self):
        username = self.e1.get()
        password = self.e2.get()
        if "@" not in username:
            messagebox.showerror("Error", "Username must contain '@'.")
            self.result = None
        else:
            self.result = (username, password)

def add_password_popup():
    
    root= tk.Tk()
    root.withdraw()
    
    dlg = CustomDialog(root)
    if dlg.result:
        username, password = dlg.result
        add_password(conn, username, password)
        print("Password added successfully!")

def delete_password_popup():
    username = simpledialog.askstring("Delete Password", "Enter the username to delete its password:")
    if username:
        delete_password(conn, username)
        print("Password deleted successfully!")

def main():
    global conn
    conn = create_connection()
    if conn is None:
        print("Error: Could not connect to the database.")
        return

    create_table(conn)

    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    while True:
        choice = simpledialog.askinteger("Password Manager", "1. Add new password\n2. Delete existing password\n3. Exit",
                                         minvalue=1, maxvalue=3)

        # Check if the user clicked 'Cancel' or the 'X' button
        if choice is None:
            print("Exiting the Password Manager. Goodbye!")
            break

        if choice == 1:
            add_password_popup()
        elif choice == 2:
            delete_password_popup()
        elif choice == 3:
            print("Exiting the Password Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()
