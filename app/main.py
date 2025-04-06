import os.path
import socket  # noqa: F401
import threading
from dataclasses import dataclass
import re
import argparse

HTTP___NOT_FOUND_ = b"HTTP/1.1 404 Not Found\r\n\r\n"

ENCODING = 'utf-8'


@dataclass
class ServerArguments:
    file_dir: str

@dataclass
class HttpRequest:
    method: str
    path: str
    protocol: str
    host: str
    host: str
    user_agent: str
    accept: str


def handle_file(request_data: HttpRequest, server_args: ServerArguments) -> bytes:
    file_name = request_data.path.replace("/files/", server_args.file_dir)
    if not os.path.isfile(file_name):
        return HTTP___NOT_FOUND_
    size = os.path.getsize(file_name)
    with open(file_name, 'rb') as file:
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {size}\r\n\r\n".encode(ENCODING) + file.read()


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
    return HttpRequest(method, path, protocol, more_parts_dict.get('HOST', None), more_parts_dict.get('User-Agent', None), more_parts_dict.get('Accept', None))

def handle_request_content(request_data: HttpRequest, server_args: ServerArguments ) -> bytes:
    if request_data.path == '/':
        return b"HTTP/1.1 200 OK\r\n\r\n"
    if request_data.path.startswith("/echo/"):
        return handle_echo(request_data)
    if request_data.path.startswith('/files/'):
        return handle_file(request_data, server_args)
    if request_data.path == "/user-agent":
        return handle_user_agent(request_data)


    return HTTP___NOT_FOUND_

def handle_request(conn: socket, server_args: ServerArguments):
    data = conn.recv(1024)
    request_data = parse_http_request(data)
    conn.sendall(handle_request_content(request_data, server_args))


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-d', '--directory')  # option that takes a value
    args = parser.parse_args()
    server_args = ServerArguments(args.directory)

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_request, args=(conn, server_args)).start()






if __name__ == "__main__":
    main()
