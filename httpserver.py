import socket
import threading
import os
import mimetypes

def handle_client(client_socket, request_number):
    request_data = client_socket.recv(1024).decode('utf-8')
    
    if not request_data:
        client_socket.close()
        return
    
    request_lines = request_data.split('\r\n')
    request_method = request_lines[0].split(' ')[0]
    requested_file = request_lines[0].split(' ')[1]
    
    if requested_file == '/favicon.ico':
        client_socket.close()
        return
    
    print(f"Request #{request_number}")
    print(">>Received request")
    print("\t" + request_data.replace("\r\n", "\r\n\t"))
    print(">>")
    
    if request_method == 'GET':
        if requested_file == '/':
            requested_file = '/index.html'
        file_path = 'htdocs' + requested_file

        if os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'

            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n"
            
            if mimetypes.guess_type(file_path)[0].startswith('image/') or mime_type.startswith('application/pdf') or mime_type.startswith('video/'):
                with open(file_path, 'rb') as file:
                    file_contents = file.read()
                response_body = file_contents
                print(f"<<Sending GET Response")
                print("\t" + response_header.replace("\r\n", "\r\n\t") + f"Content-Length: {len(response_body)}")
                if not mime_type.startswith('text/html'):
                    print(f"\t[Binary Data of length: {len(response_body)}]")
                print("<<")
            else:
                with open(file_path, 'r') as file:
                    file_contents = file.read()

                response_body = file_contents.encode('utf-8')
                print(f"<<Sending GET Response")
                print("\t" + response_header.replace("\r\n", "\r\n\t") + f"Content-Length: {len(response_body)}")
                print("<<")
        else:
            response_header = "HTTP/1.1 404 NOT FOUND\r\n"
            response_body = b""
            print(f"<<Sending GET Response")
            print("\t" + response_header.replace("\r\n", "\r\n\t") + "[Binary Data of length: 0]")
            print("<<")
    elif request_method == 'POST':
        if requested_file == '/form_submitted':
            user_input = request_data.split('\r\n')[-1]
            user = user_input.split('=')[1]
            response_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
            response_body = f"<h1 style='color: black;'>Hi, <span style='color: red;'>{user}</span></h1>".encode('utf-8')
            print(f"<<Sending POST Response")
            print("\t" + response_header.replace("\r\n", "\r\n\t"))
            print("<<")
        else:
            response_header = "HTTP/1.1 404 NOT FOUND\r\n"
            response_body = b""
            print(f"<<Sending POST Response")
            print("\t" + response_header.replace("\r\n", "\r\n\t") + "[Binary Data of length: 0]")
            print("<<")
    else:
        response_header = "HTTP/1.1 501 Not Implemented\r\nContent-Type: text/html\r\n"
        response_body = b"<h1>501 Not Implemented</h1>"
        print(f"<<Sending GET/POST Response")
        print("\t" + response_header.replace("\r\n", "\r\n\t") + "[Binary Data of length: 0]")
        print("<<")
    
    response = response_header + f"Content-Length: {len(response_body)}\r\n\r\n"
    
    client_socket.sendall(response.encode('utf-8'))
    client_socket.sendall(response_body)
    client_socket.close()

def main():
    server_host = 'localhost'
    server_port = 8000
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    
    print(f"Server listening on {server_host}:{server_port}")

    request_counter = 0
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            request_counter += 1
            client_thread = threading.Thread(target=handle_client, args=(client_socket, request_counter))
            client_thread.start()
    except KeyboardInterrupt:
        server_socket.close()
        print("Server closed.")

if __name__ == "__main__":
    main()