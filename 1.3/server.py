import socket
from sys import byteorder
from zlib import adler32 as a32


SERVER_HOST = "z33_server_py"
SERVER_PORT = 8080


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))

    print(f"Listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        data, addr = server_socket.recvfrom(1024) 
        if verify_data(data):
            seq_no = data[0]
            response = seq_no.to_bytes(1, byteorder="big") + b"OK\0"
        else:
            response = b"FAIL"
        print(f"Received #{data[0]} from {addr}; responding with {response}")
        server_socket.sendto(response, addr)  # Odsyłanie odpowiedzi do klienta


def verify_checksum(data):
    # Message format: 1B seq_no + 2B lenght + 4B checksum + message
    return (data[3:7] == a32(data[7:]).to_bytes(4, byteorder="big"))


def verify_data(data):
    if len(data) >= 3 and data[1:3] == len(data[7:]).to_bytes(2, byteorder="big"):
        if verify_checksum(data):
            return True
    return False


if __name__ == "__main__":
    main()
