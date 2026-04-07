import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json, os, base64
from cryptography.fernet import Fernet
import hashlib

DATA_FILE = "passwords.json"

# ---------- HASH ----------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ---------- KEY ----------
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

# ---------- FILE ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- SET MASTER ----------
def setup_master():
    data = load_data()
    if "master" not in data:
        master = simpledialog.askstring("Set Master Password", "Enter Master Password:", show="*")
        if not master:
            messagebox.showerror("Error", "Master password required!")
            root.destroy()
            return
        data["master"] = hash_password(master)
        data["credentials"] = []
        save_data(data)

# ---------- LOGIN ----------
def login():
    global cipher

    data = load_data()
    entered = entry_login.get()

    if hash_password(entered) == data.get("master"):
        key = generate_key(entered)
        cipher = Fernet(key)
        messagebox.showinfo("Success", "Login Successful!")
        open_dashboard()
    else:
        messagebox.showerror("Error", "Wrong Master Password!")

# ---------- ADD ----------
def add_password():
    website = entry_site.get()
    username = entry_user.get()
    password = entry_pass.get()

    if not website or not username or not password:
        messagebox.showwarning("Warning", "Fill all fields!")
        return

    encrypted = cipher.encrypt(password.encode()).decode()

    data = load_data()
    data["credentials"].append({
        "website": website,
        "username": username,
        "password": encrypted
    })

    save_data(data)

    entry_site.delete(0, tk.END)
    entry_user.delete(0, tk.END)
    entry_pass.delete(0, tk.END)

    messagebox.showinfo("Saved", "Password stored securely!")

# ---------- VIEW ----------
def view_passwords():
    data = load_data()

    if not data.get("credentials"):
        messagebox.showinfo("Info", "No passwords saved yet!")
        return

    win = tk.Toplevel(root)
    win.title("Saved Passwords")
    win.geometry("450x300")

    tree = ttk.Treeview(win, columns=("Website", "Username", "Password"), show="headings")
    tree.heading("Website", text="Website")
    tree.heading("Username", text="Username")
    tree.heading("Password", text="Password")

    for item in data.get("credentials", []):
        try:
            decrypted = cipher.decrypt(item["password"].encode()).decode()
        except:
            decrypted = "❌ Wrong master password"

        tree.insert("", "end", values=(item['website'], item['username'], decrypted))

    tree.pack(fill="both", expand=True)

# ---------- DELETE ----------
def delete_password():
    data = load_data()

    if not data.get("credentials"):
        messagebox.showinfo("Info", "Nothing to delete!")
        return

    index = simpledialog.askinteger("Delete", "Enter index to delete (see View list):")

    if index is None or index <= 0 or index > len(data["credentials"]):
        messagebox.showerror("Error", "Invalid index!")
        return

    data["credentials"].pop(index - 1)
    save_data(data)

    messagebox.showinfo("Deleted", "Entry removed!")

# ---------- SEARCH ----------
def search_password():
    query = simpledialog.askstring("Search", "Enter website name:")
    data = load_data()

    if not query:
        return

    results = []

    for item in data.get("credentials", []):
        if query.lower() in item["website"].lower():
            try:
                decrypted = cipher.decrypt(item["password"].encode()).decode()
            except:
                decrypted = "❌ Cannot decrypt"

            results.append((item['website'], item['username'], decrypted))

    if not results:
        messagebox.showinfo("Not Found", "No matching entries!")
        return

    win = tk.Toplevel(root)
    win.title("Search Results")
    win.geometry("450x250")

    tree = ttk.Treeview(win, columns=("Website", "Username", "Password"), show="headings")
    tree.heading("Website", text="Website")
    tree.heading("Username", text="Username")
    tree.heading("Password", text="Password")

    for row in results:
        tree.insert("", "end", values=row)

    tree.pack(fill="both", expand=True)

# ---------- TOGGLE PASSWORD ----------
def toggle_password():
    if entry_pass.cget('show') == '':
        entry_pass.config(show='*')
        btn_toggle.config(text='Show')
    else:
        entry_pass.config(show='')
        btn_toggle.config(text='Hide')

# ---------- DASHBOARD ----------
def open_dashboard():
    dash = tk.Toplevel(root)
    dash.title("Dashboard")
    dash.geometry("400x420")

    frame = ttk.Frame(dash, padding=20)
    frame.pack(fill="both", expand=True)

    global entry_site, entry_user, entry_pass, btn_toggle

    ttk.Label(frame, text="Password Manager", font=("Segoe UI", 16, "bold")).pack(pady=10)

    ttk.Label(frame, text="Website").pack(anchor="w")
    entry_site = ttk.Entry(frame)
    entry_site.pack(fill="x", pady=5)

    ttk.Label(frame, text="Username").pack(anchor="w")
    entry_user = ttk.Entry(frame)
    entry_user.pack(fill="x", pady=5)

    ttk.Label(frame, text="Password").pack(anchor="w")

    row = ttk.Frame(frame)
    row.pack(fill="x", pady=5)

    entry_pass = ttk.Entry(row, show="*")
    entry_pass.pack(side="left", fill="x", expand=True)

    btn_toggle = ttk.Button(row, text="Show", command=toggle_password)
    btn_toggle.pack(side="left", padx=5)

    ttk.Button(frame, text="Add", command=add_password).pack(fill="x", pady=6)
    ttk.Button(frame, text="View", command=view_passwords).pack(fill="x", pady=6)
    ttk.Button(frame, text="Search", command=search_password).pack(fill="x", pady=6)
    ttk.Button(frame, text="Delete", command=delete_password).pack(fill="x", pady=6)

# ---------- MAIN ----------
root = tk.Tk()
root.title("Password Manager")
root.geometry("350x250")
root.resizable(False, False)

setup_master()

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

ttk.Label(frame, text="🔐 Password Manager", font=("Segoe UI", 16, "bold")).pack(pady=10)

ttk.Label(frame, text="Enter Master Password").pack()
entry_login = ttk.Entry(frame, show="*")
entry_login.pack(fill="x", pady=5)

ttk.Button(frame, text="Login", command=login).pack(pady=15)

root.mainloop()