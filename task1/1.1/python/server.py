import socket
from zlib import adler32 as a32
from client import prep_msg


def main():
    server_ip = "127.0.0.1"
    server_port = 8081

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    print(f"Serwer nasłuchuje na {server_ip}:{server_port}")

    while True:
        data, addr = server_socket.recvfrom(1024)  # Odbieranie danych z klienta
        if verify_data(data):  # Weryfikacja odebranych danych
            response = "OK"
            print(f"Odebrano poprawne dane od {addr}")
        else:
            response = "FAIL"
            print(f"Odebrano niepoprawne dane od {addr}")
        print(data[6:].decode())
        # Odsyłanie odpowiedzi do klienta
        server_socket.sendto(prep_msg(response), addr)


def verify_checksum(data, msg_len):
    return data[2:6] == a32(data[6:msg_len+6]).to_bytes(4, byteorder="big")


def verify_data(data):
    # Weryfikacja długości datagramu i zawartości

    msg_len = int.from_bytes(data[:2], "big")
    if len(data) >= 2 and data[:2] == len(data[6:msg_len+6]).to_bytes(2, byteorder="big"):
        if verify_checksum(data, msg_len):
            return True
    return False


if __name__ == "__main__":
    main()
