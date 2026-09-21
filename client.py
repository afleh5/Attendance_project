
import socket
import time
import tkinter as tk
from tkinter import messagebox

BG = "#0B1220"
CARD = "#111827"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#38BDF8"
DARK = "#0284C7"
ENTRY = "#1E293B"

current_user_id = None
current_user_role = None

def send_request(data):

    for attempt in range(3):

        client = socket.socket()

        try:
            client.settimeout(5)
            client.connect(("localhost", 1234))
            client.send(data.encode())
            response = client.recv(4096).decode()
            client.close()
            return response

        except (ConnectionRefusedError, socket.timeout):
            client.close()

            if attempt < 2:
                time.sleep(1)
            else:
                messagebox.showerror(
                    "Connection Error",
                    "Unable to connect to the server.\nPlease make sure the server is running."
                )
                return ""

        except Exception as error:
            client.close()
            messagebox.showerror("Connection Error", str(error))
            return ""

def style(window, title, size):

    window.title(title)
    window.geometry(size)
    window.resizable(False, False)
    window.configure(bg=BG)

def button(parent, text, command, secondary=False):

    bg = "#334155" if secondary else DARK
    active = "#475569" if secondary else ACCENT

    return tk.Button(
        parent,
        text=text,
        width=32,
        height=2,
        bg=bg,
        fg=TEXT,
        activebackground=active,
        activeforeground=TEXT,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        command=command
    )

def show_table(title, headers, widths, rows, size):

    win = tk.Toplevel()
    style(win, title, size)

    tk.Label(
        win, text=title.upper(), bg=CARD, fg=ACCENT,
        font=("Arial", 24, "bold")
    ).pack(fill="x", pady=25)

    frame = tk.Frame(win, bg=BG)
    frame.pack(padx=25, pady=20)

    for column, header in enumerate(headers):
        tk.Label(
            frame, text=header, width=widths[column],
            bg=DARK, fg=TEXT, font=("Arial", 10, "bold")
        ).grid(row=0, column=column, padx=1, pady=1)

    for row_number, row in enumerate(rows, start=1):
        for column, value in enumerate(row):
            bg = CARD if row_number % 2 else ENTRY
            tk.Label(
                frame, text=value, width=widths[column],
                bg=bg, fg=TEXT, font=("Arial", 10)
            ).grid(row=row_number, column=column, padx=1, pady=1)

    button(win, "CLOSE", win.destroy, True).pack(pady=20)

def login():

    global current_user_id, current_user_role

    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Warning", "Please enter username and password")
        return

    response = send_request("LOGIN:" + username + "|" + password)

    if response.startswith("Login successful"):
        parts = response.split("|")
        current_user_id = parts[1]
        current_user_role = parts[2]
        window.destroy()

        if current_user_role == "admin":
            admin_dashboard()
        else:
            student_dashboard()

    elif response != "":
        messagebox.showerror("Login Failed", "Invalid username or password")

def add_user():

    username = user_username.get()
    password = user_password.get()
    full_name = user_full_name.get()

    if username == "" or password == "" or full_name == "":
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    response = send_request(
        "ADD_USER:" + username + "|" + password + "|" + full_name
    )

    if response == "User added successfully":
        messagebox.showinfo("Add User", "User added successfully")
        user_username.delete(0, tk.END)
        user_password.delete(0, tk.END)
        user_full_name.delete(0, tk.END)

    elif response == "Username already exists":
        messagebox.showerror("Add User", "Username already exists")

def add_user_window():

    global user_username, user_password, user_full_name

    win = tk.Toplevel()
    style(win, "Add Student", "620x610")

    tk.Label(
        win, text="ADD NEW STUDENT", bg=CARD, fg=ACCENT,
        font=("Arial", 24, "bold")
    ).pack(fill="x", pady=30)

    form = tk.Frame(win, bg=BG)
    form.pack(padx=80)

    entries = []

    for text, show in [("USERNAME", ""), ("PASSWORD", "*"), ("FULL NAME", "")]:
        tk.Label(form, text=text, bg=BG, fg=TEXT).pack(anchor="w")
        entry = tk.Entry(
            form, width=38, bg=ENTRY, fg=TEXT,
            insertbackground=TEXT, relief="flat", show=show
        )
        entry.pack(pady=(5, 18), ipady=7)
        entries.append(entry)

    user_username, user_password, user_full_name = entries

    button(form, "ADD STUDENT", add_user).pack(pady=5)
    button(form, "CLOSE", win.destroy, True).pack(pady=10)

def view_users():

    response = send_request("VIEW_USERS:")

    if not response:
        return

    if response == "NO_USERS":
        messagebox.showinfo("Users", "No users found")
        return

    rows = [line.split("|") for line in response.strip().splitlines()]

    show_table(
        "Users List",
        ["ID", "USERNAME", "FULL NAME", "ROLE"],
        [10, 22, 28, 15], rows, "930x600"
    )

def mark_attendance():

    response = send_request(
        "MARK_ATTENDANCE:" + str(current_user_id)
    )

    if response == "Attendance marked successfully":
        messagebox.showinfo("Attendance", "Attendance marked successfully")

    elif response == "Attendance already marked":
        messagebox.showwarning(
            "Attendance",
            "You have already marked attendance today"
        )

def attendance_history():

    response = send_request(
        "ATTENDANCE_HISTORY:" + str(current_user_id)
    )

    if not response:
        return

    if response == "NO_ATTENDANCE":
        messagebox.showinfo("Attendance History", "No attendance records found")
        return

    rows = [line.split("|") for line in response.strip().splitlines()]

    show_table(
        "Attendance History",
        ["DATE", "TIME", "STATUS"],
        [25, 25, 25], rows, "850x570"
    )

def attendance_records():

    response = send_request("ATTENDANCE_RECORDS:")

    if not response:
        return

    if response == "NO_ATTENDANCE":
        messagebox.showinfo("Attendance Records", "No attendance records found")
        return

    rows = [line.split("|") for line in response.strip().splitlines()]

    show_table(
        "Attendance Records",
        ["FULL NAME", "USERNAME", "DATE", "TIME", "STATUS"],
        [24, 20, 20, 18, 18], rows, "1180x620"
    )

def admin_dashboard():

    win = tk.Tk()
    style(win, "Admin Dashboard", "760x620")

    tk.Label(
        win, text="ADMIN DASHBOARD", bg=CARD, fg=ACCENT,
        font=("Arial", 27, "bold")
    ).pack(fill="x", pady=35)

    body = tk.Frame(win, bg=BG)
    body.pack(fill="both", expand=True, padx=45, pady=25)

    for text, command in [
        ("ADD STUDENT", add_user_window),
        ("VIEW USERS", view_users),
        ("ATTENDANCE RECORDS", attendance_records),
        ("LOGOUT", win.destroy)
    ]:
        button(body, text, command, text == "LOGOUT").pack(pady=8)

    win.mainloop()

def student_dashboard():

    win = tk.Tk()
    style(win, "Student Dashboard", "760x560")

    tk.Label(
        win, text="STUDENT DASHBOARD", bg=CARD, fg=ACCENT,
        font=("Arial", 27, "bold")
    ).pack(fill="x", pady=35)

    body = tk.Frame(win, bg=BG)
    body.pack(fill="both", expand=True, padx=45, pady=25)

    for text, command in [
        ("MARK ATTENDANCE", mark_attendance),
        ("ATTENDANCE HISTORY", attendance_history),
        ("LOGOUT", win.destroy)
    ]:
        button(body, text, command, text == "LOGOUT").pack(pady=10)

    win.mainloop()



window = tk.Tk()
style(window, "Attendance System", "550x500")

card = tk.Frame(window, bg=CARD)
card.pack(padx=55, pady=35, fill="both", expand=True)

tk.Label(
    card, text="ATTENDANCE SYSTEM", bg=CARD, fg=ACCENT,
    font=("Arial", 26, "bold")
).pack(pady=40)

for text in ["Username", "Password"]:
    tk.Label(card, text=text, bg=CARD, fg=TEXT).pack(pady=5)
    entry = tk.Entry(
        card, width=35, bg=ENTRY, fg=TEXT,
        insertbackground=TEXT, relief="flat",
        show="*" if text == "Password" else ""
    )
    entry.pack(ipady=6)

    if text == "Username":
        username_entry = entry
    else:
        password_entry = entry

button(card, "LOGIN", login).pack(pady=35)

window.mainloop()
