
import mysql.connector



DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "attendance_system"



def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )



if __name__ == "__main__":

    try:

        connection = get_connection()

        print("MySQL connection successful!")

        connection.close()

    except mysql.connector.Error as error:

        print("MySQL connection failed:")
        print(error)
