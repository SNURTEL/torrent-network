import socket
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
            response = b"OK"
        else:
            response = b"FAIL"
        print(f"Received {data[:8]}[...] from {addr}; responding with {response}")
        server_socket.sendto(response, addr)  # Odsyłanie odpowiedzi do klienta


def verify_checksum(data):
    # Message format: 2B lenght + 4B checksum + message
    return (data[2:6] == a32(data[6:]).to_bytes(4, byteorder="big"))


def verify_data(data):
    if len(data) >= 2 and data[:2] == len(data[6:]).to_bytes(2, byteorder="big"):
        if verify_checksum(data):
            return True
    return False


if __name__ == "__main__":
    main()
