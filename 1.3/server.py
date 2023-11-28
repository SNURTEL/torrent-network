import socket
from zlib import adler32 as a32


def main():
    server_host = "z33_server_py"
    server_port = 8080

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_host, server_port))

    print(f"Serwer nasłuchuje na {server_host}:{server_port}")

    while True:
        data, addr = server_socket.recvfrom(1024)  # Odbieranie danych z klienta
        if verify_data(data):  # Weryfikacja odebranych danych
            response = b"OK"
            print(f"Odebrano poprawne dane od {addr}")
        else:
            response = b"FAIL"
            print(f"Odebrano niepoprawne dane od {addr}")
        server_socket.sendto(response, addr)  # Odsyłanie odpowiedzi do klienta


def verify_checksum(data):
    return (data[2:6] == a32(data[6:]).to_bytes(4, byteorder="big"))


def verify_data(data):
    print(data)
    if len(data) >= 2 and data[:2] == len(data[6:]).to_bytes(2, byteorder="big"):
        if verify_checksum(data):
            return True
    return False


if __name__ == "__main__":
    main()
