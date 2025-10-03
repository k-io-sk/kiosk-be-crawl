from db import get_conn, show_tables
def main():
    conn = get_conn()
    show_tables(conn)


if __name__ == "__main__":
    main()