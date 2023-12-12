import socket
import struct
import sys
import io


HOST_DEFAULT = '0.0.0.0'
BUFSIZE = 512


def unpack_data(data):
    # Unpack the received data
    unpacked_data = struct.unpack('!H L 20s', data)
    short_num, int_num, string_data = unpacked_data
    return short_num, int_num, string_data.decode('utf-8').rstrip('\x00')

def main():
    if len(sys.argv) < 3:
        print(f"Using :{port}")
        host = HOST_DEFAULT
        port = 8000
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
            data = client_socket.recv(1024)
            if not data:
                break

            # Unpack and print data
            short_num, int_num, string_data = unpack_data(data)
            print(f"Received data: Short Num: {short_num}, Int Num: {int_num}, String: {string_data}")
        client_socket.close()

if __name__ == "__main__":
    main()
