import socket
import signal
import sys


def init_socket():
    host = "localhost"
    port = 8080

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((host, port))
    soc.listen(5)

    print(f"Server is listening on port {port}")

    return soc


def send_301_status(client_socket):
    response = (
        "HTTP/1.1 301 Moved Permanently\r\n"
        "Location: https://localhost:8443/\r\n"
        "Content-Length: 0\r\n"
        "\r\n"
    )

    client_socket.send(response.encode())
    client_socket.close()


def send_500_status(ssl_client_socket, exception):
    response_body = f"An error occurred: {exception}"
    response = (
        f"HTTP/1.1 500 Internal Server Error\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "\r\n"
        f"<h1>500 Internal Server Error</h1><p>{response_body}</p>"
    )

    ssl_client_socket.send(response.encode())
    ssl_client_socket.close()


def handle_signal(signal, frame):
    print("Server interrupted. Closing socket...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    soc = init_socket()

    try:
        while True:
            client_socket, client_address = soc.accept()
            print(f"Connection from {client_address}")

            try:
                send_301_status(client_socket)

            except Exception as e:
                send_500_status(client_socket, e)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        soc.close()


if __name__ == "__main__":
    main()
