import sys
import mysql.connector

def main():
  try:
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="users",
      port=3306,
      connect_timeout=5,
    )
  except mysql.connector.Error as err:
    print("MySQL connection failed:", err)
    print()
    print("Common causes:")
    print(" - MySQL server is not running on this host/port.")
    print(" - Credentials are incorrect (user/password).")
    print(" - 'localhost' resolved to a socket; we used 127.0.0.1 to force TCP.")
    print()
    print("Quick fixes:")
    print(" - Start MySQL: sudo systemctl start mysql  (or mysqld on some systems)")
    print(" - Install MySQL server if missing: sudo apt install mysql-server")
    print(" - Run a temporary MySQL in Docker:")
    print("     docker run --name mysql-local -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=users -p 3306:3306 -d mysql:8.0")
    sys.exit(1)

  my_cursor = mydb.cursor()
  my_cursor.execute("CREATE DATABASE IF NOT EXISTS our_users")

  my_cursor.execute("SHOW DATABASES")

  for db in my_cursor:
    print(db)


if __name__ == '__main__':
  main()