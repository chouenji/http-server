import socket
import ssl
import signal
import sys


def init_socket():
    host = "localhost"
    port = 8443

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((host, port))
    soc.listen(5)

    print(f"Server is listening on port {port}")

    return soc


def init_ssl():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain("cert.pem", "key.pem")

    return context


def read_file(file: str):
    with open(file, "r") as file_content:
        return file_content.read()


def create_response(content: str, content_type: str):
    content_length = len(content)
    return (
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {content_length}\r\n"
        f"\r\n"
        f"{content}"
    )


def send_400_status(ssl_client_socket):
    response_body = (
        "<h1>400 Bad Request</h1><p>Your request could not be processed.</p>"
    )

    content_length = len(response_body)

    response = (
        f"HTTP/1.1 400 Bad Request\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {content_length}\r\n"
        "\r\n"
        f"{response_body}"
    )

    ssl_client_socket.send(response.encode())
    ssl_client_socket.close()


def send_404_status(ssl_client_socket):
    response_body = (
        "<h1>404 Not Found</h1><p>File not found or file type not specified.</p>"
    )

    content_length = len(response_body)

    response = (
        f"HTTP/1.1 404 Not Found\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {content_length}\r\n"
        "\r\n"
        f"{response_body}"
    )

    ssl_client_socket.send(response.encode())
    ssl_client_socket.close()


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

    context = init_ssl()

    try:
        while True:
            client_socket, client_address = soc.accept()
            print(f"Connection from {client_address}")

            ssl_client_socket = context.wrap_socket(client_socket, server_side=True)

            try:
                request_data = ssl_client_socket.recv(1024).decode()
                print("Received request:")
                print(request_data)

                if "GET" in request_data:
                    headers = request_data.split("\r\n")

                    for header in headers:
                        if header.lower().startswith("accept:"):
                            content_type = header.split(":", 1)[1].strip()
                            match content_type:
                                case "text/css":
                                    response = read_file("style.css")
                                    ssl_client_socket.send(
                                        create_response(response, "text/css").encode()
                                    )

                                case "application/javascript":
                                    response = read_file("script.js")
                                    ssl_client_socket.send(
                                        create_response(
                                            response, "application/javascript"
                                        ).encode()
                                    )

                                case _:
                                    response = read_file("index.html")
                                    ssl_client_socket.send(
                                        create_response(response, "text/html").encode()
                                    )

                else:
                    send_400_status(ssl_client_socket)

            except Exception as e:
                send_500_status(ssl_client_socket, e)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        soc.close()


if __name__ == "__main__":
    main()
