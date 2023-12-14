import socket
import struct
import sys
import io


HOST_DEFAULT = '0.0.0.0'
BUFSIZE = 512


import struct

def unpack_int(data):
    # Unpack the received data
    list_length = struct.unpack('<I', data)[0]
    return list_length


def unpack_str(data):
    # Unpack the received data
    list_length = struct.unpack('<S', data)[0]
    return list_length


def receive_linked_list(client_socket, list_length):
    linked_list = []
    for _ in range(list_length):
        node = receive_node(client_socket)
        linked_list.append(node)
    return linked_list

def receive_node(client_socket):
    _ = client_socket.recv(4)
    short_int = client_socket.recv(2)
    long_int = unpack_int(client_socket.recv(4))
    fixed_string = client_socket.recv(4)
    string_length = unpack_int(client_socket.recv(4))
    dynamic_string = client_socket.recv(string_length)

    return (short_int, long_int, fixed_string, string_length, dynamic_string)

def main():
    if len(sys.argv) < 3:
        host = HOST_DEFAULT
        port = 8000
        print(f"Using :{port}")
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        print("Using {}:{}".format(host, port))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST_DEFAULT, port))
        server_socket.listen(5)

        print(f"Server listening on port {port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # Receive data
            list_length_data = client_socket.recv(4)
            if not list_length_data:
                break
            list_length = unpack_int(list_length_data)

            # Receive linked list
            linked_list = receive_linked_list(client_socket, list_length)
            print("Received linked list:")
            print(linked_list)
        

if __name__ == "__main__":
    main()
