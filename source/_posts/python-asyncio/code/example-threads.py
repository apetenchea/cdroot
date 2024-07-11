import socket
import threading


def handle_client(conn):
    with conn:
        while True:
            payload = conn.recv(1024)
            if not payload:
                break
            num = payload.decode('utf-8')
            try:
                result = hex(int(num))
            except ValueError:
                result = 'Request payload must be an integer'
            result += '\n'
            conn.sendall(result.encode('utf-8'))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 65432))
        s.listen()
        while True:
            conn, _ = s.accept()
            client = threading.Thread(target=handle_client, args=(conn,))
            client.start()


if __name__ == '__main__':
    main()
