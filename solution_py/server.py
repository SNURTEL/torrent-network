import socket
from zlib import adler32 as a32


def main():
    server_ip = "127.0.0.1"
    server_port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    print(f"Serwer nasłuchuje na {server_ip}:{server_port}")

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
    # print(data[2:6])
    # print(a32(data[6:]).to_bytes(4, byteorder="big"))
    return (data[2:6] == a32(data[6:]).to_bytes(4, byteorder="big"))


def verify_data(data):
    print(data)
    # Weryfikacja długości datagramu i zawartości
    if len(data) >= 2 and data[:2] == len(data[6:]).to_bytes(2, byteorder="big"):
        if verify_checksum(data):
            return True
    return False


if __name__ == "__main__":
    main()
