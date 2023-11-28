import socket
import sys
from zlib import adler32 as a32


def main(message=None):
    server_ip = "127.0.0.1"
    server_port = 8080

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = prep_msg(message)

    client_socket.sendto(data, (server_ip, server_port))  # Wysyłanie danych do serwera

    response, addr = client_socket.recvfrom(1024)  # Odbieranie odpowiedzi od serwera
    print(f"Odpowiedź od serwera: {response[6:].decode()}")


def prep_msg(msg=None):
    if msg is not None:
        data = bytearray((ord(letter) for letter in msg + "\0"))
    else:
        data_length = 10  # Długość danych bez uwzględnienia nagłówka
        data = bytearray(
            [i % 26 + 65 for i in range(data_length - 1)]
        )  # Generowanie danych A-Z
        data.append(ord("\0"))


    checksum = a32(data).to_bytes(4, byteorder="big")
    # print(checksum)
    # Dodanie nagłówka z informacją o długości
    data = len(data).to_bytes(2, byteorder="big") + checksum + data
    data.zfill(1024-len(data))
    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()