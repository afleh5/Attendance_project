
import socket
import threading
import hashlib

from datetime import datetime
from database import get_connection


def send(conn, text):

    conn.send(text.encode())


def read_query(sql, values=()):

    db = get_connection()
    cur = db.cursor()
    cur.execute(sql, values)
    rows = cur.fetchall()
    cur.close()
    db.close()

    return rows


def write_query(sql, values=()):

    db = get_connection()
    cur = db.cursor()
    cur.execute(sql, values)
    db.commit()
    cur.close()
    db.close()


def records_text(records):

    text = ""

    for record in records:

        text += "|".join(
            str(value)
            for value in record
        ) + "\n"

    return text


# 
# CLIENT REQUEST


def handle_client(conn, addr):

    print(
        "Client connected:",
        addr
    )

    try:

        data = conn.recv(4096).decode()
        command, information = data.split(":", 1)

  
        if command == "LOGIN":

            username, password = information.split("|")

            password = hashlib.sha256(
                password.encode()
            ).hexdigest()

            users = read_query(
                "SELECT id, username, password, role "
                "FROM users WHERE username = %s "
                "AND password = %s",
                (username, password)
            )

            if users:

                user = users[0]

                send(
                    conn,
                    "Login successful|" +
                    str(user[0]) + "|" +
                    user[3]
                )

                print(
                    "Login successful:",
                    username
                )

            else:

                send(
                    conn,
                    "Login failed"
                )

        # ADD USER
        elif command == "ADD_USER":

            username, password, full_name = information.split("|")

            password = hashlib.sha256(
                password.encode()
            ).hexdigest()

            users = read_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            if users:

                send(
                    conn,
                    "Username already exists"
                )

            else:

                write_query(
                    "INSERT INTO users "
                    "(username, password, full_name, role) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        username,
                        password,
                        full_name,
                        "student"
                    )
                )

                send(
                    conn,
                    "User added successfully"
                )

        # VIEW USERS
        elif command == "VIEW_USERS":

            users = read_query(
                "SELECT id, username, full_name, role "
                "FROM users"
            )

            send(
                conn,
                records_text(users)
                if users else "NO_USERS"
            )

        # MARK ATTENDANCE
        elif command == "MARK_ATTENDANCE":

            today = datetime.now().date()
            now = datetime.now().time()

            records = read_query(
                "SELECT id FROM attendance "
                "WHERE user_id = %s AND attendance_date = %s",
                (information, today)
            )

            if records:

                send(
                    conn,
                    "Attendance already marked"
                )

            else:

                write_query(
                    "INSERT INTO attendance "
                    "(user_id, attendance_date, attendance_time, status) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        information,
                        today,
                        now,
                        "Present"
                    )
                )

                send(
                    conn,
                    "Attendance marked successfully"
                )

        # ATTENDANCE HISTORY
        elif command == "ATTENDANCE_HISTORY":

            records = read_query(
                "SELECT attendance_date, attendance_time, status "
                "FROM attendance WHERE user_id = %s "
                "ORDER BY attendance_date DESC, attendance_time DESC",
                (information,)
            )

            send(
                conn,
                records_text(records)
                if records else "NO_ATTENDANCE"
            )

        # ATTENDANCE RECORDS
        elif command == "ATTENDANCE_RECORDS":

            records = read_query(
                "SELECT users.full_name, users.username, "
                "attendance.attendance_date, "
                "attendance.attendance_time, attendance.status "
                "FROM attendance INNER JOIN users "
                "ON attendance.user_id = users.id "
                "ORDER BY attendance.attendance_date DESC, "
                "attendance.attendance_time DESC"
            )

            send(
                conn,
                records_text(records)
                if records else "NO_ATTENDANCE"
            )

    # Error Handling 
    except Exception as error:

        print(
            "Client error:",
            error
        )

        try:

            send(
                conn,
                "Server error"
            )

        except:

            pass

    # CLOSE
    finally:

        conn.close()

        print(
            "Client disconnected:",
            addr
        )

# SERVER START
server = socket.socket()

server.bind(
    ("localhost", 1234)
)

server.listen(5)

print(
    "Server is running..."
)

# Accept Multiple Clients
while True:

    conn, addr = server.accept()

    client_thread = threading.Thread(
        target=handle_client,
        args=(conn, addr)
    )

    client_thread.start()
