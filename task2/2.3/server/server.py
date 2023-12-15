import os
import socket
import struct

HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("SERVER_PORT", "8000"))


def receive_linked_list(client_socket, list_length):
    linked_list = []
    for _ in range(list_length):
        node = receive_node(client_socket)
        print(node)
        linked_list.append(node)
    return linked_list


def receive_node(client_socket):
    raw_data = client_socket.recv(28)
    unpacked_data = struct.unpack('<8sHxxI6sxxI', raw_data)

    short_int = unpacked_data[1]
    long_int = unpacked_data[2]
    fixed_string = unpacked_data[3].decode()
    dynamic_string_length = unpacked_data[4]
    if dynamic_string_length:
        recv_size = dynamic_string_length + 4
        raw_data2 = client_socket.recv(recv_size)
        unpacked_data2 = struct.unpack(f'<{dynamic_string_length}sxxxx', raw_data2)
        dynamic_string = unpacked_data2[0].decode('ASCII')
    else:
        dynamic_string = ""
    return short_int, long_int, fixed_string, dynamic_string_length, dynamic_string


def handle_connection(sock, addr):
    # Receive data
    list_length_data = sock.recv(4)
    if not list_length_data:
        return
    list_length = struct.unpack('<I', list_length_data)[0]
    print(f"List length is {list_length}")

    # Receive linked list
    linked_list = receive_linked_list(sock, list_length)
    sock.close()

    print("Received linked list:")
    for l in linked_list:
        print(l)


def main():
    print(f"Serving on {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_connection(client_socket, addr)


if __name__ == "__main__":
    main()
