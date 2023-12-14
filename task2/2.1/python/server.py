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
        print(node)
        linked_list.append(node)
    return linked_list

def receive_node(client_socket):
    raw_data = client_socket.recv(28)  # 28
    print(raw_data)
    unpacked_data = struct.unpack('<8sHxxI6sxxI', raw_data)

    # Extract the values
    next_ptr = unpacked_data[0]
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
            list_length = struct.unpack('<I', list_length_data)[0]
            print(f"List length is {list_length}")

            # Receive linked list
            linked_list = receive_linked_list(client_socket, list_length)
            print("Received linked list:")
            for l in linked_list:
                print(l)
        

if __name__ == "__main__":
    main()
