import socket  # noqa: F401
from dataclasses import dataclass
import re

ENCODING = 'utf-8'


@dataclass
class HttpRequest:
    method: str
    path: str
    protocol: str
    host: str
    host: str
    user_agent: str
    accept: str


def handle_echo(request_data: HttpRequest) -> bytes:
    arg = re.sub("^/echo/", "", request_data.path)
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(arg)}\r\n\r\n{arg}".encode(ENCODING)

def handle_user_agent(request_dat: HttpRequest):
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(request_dat.user_agent)}\r\n\r\n{request_dat.user_agent}".encode(ENCODING)


def parse_http_request(data: bytes):
    parts = data.decode(ENCODING).split(' ')
    method = parts[0]
    path = parts[1]
    protocol = parts[2].split("\r\n")[0]
    more_parts = data.decode(ENCODING).split("\r\n")[1:]
    more_parts_dict = {}
    for thingy in more_parts:
        components = thingy.split(": ")
        if components[0]:
            more_parts_dict[components[0]] = components[1]
    return HttpRequest(method, path, protocol, more_parts_dict['Host'], more_parts_dict.get('User-Agent', None), more_parts_dict.get('Accept', None))

def handle_request(request_data: HttpRequest ) -> bytes:
    if request_data.path == '/':
        return b"HTTP/1.1 200 OK\r\n\r\n"
    if request_data.path.startswith("/echo/"):
        return handle_echo(request_data)
    if request_data.path == "/user-agent":
        return handle_user_agent(request_data)


    return b"HTTP/1.1 404 Not Found\r\n\r\n"




def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    while True:
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        conn, addr = server_socket.accept()
        data = conn.recv(1024)
        request_data = parse_http_request(data)
        conn.sendall(handle_request(request_data))





if __name__ == "__main__":
    main()
