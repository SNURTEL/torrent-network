import socket
import sys
from zlib import adler32 as a32


def main(iters, growth):
    server_ip = "127.0.0.1"
    server_port = 8080

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = ""
    for i in range(0, int(iters)):
        message += "".join("A" for _ in range(int(growth)))
        data = prep_msg(message)
        client_socket.sendto(data, (server_ip, server_port))  # Wysyłanie danych do serwera
        response, addr = client_socket.recvfrom(1024)  # Odbieranie odpowiedzi od serwera
        print(f"Odpowiedź od serwera nr {i + 1}: {response[6:].decode()}")
        if str(response[6:].decode()) == "FAIL\0":
            print(f"Failed for message {len(message)} bytes long")
            break


def prep_msg(msg=None):
    data = bytearray((ord(letter) for letter in msg + "\0"))

    # Dodanie nagłówka z informacją o długości i sumie kontrolnej
    checksum = a32(data).to_bytes(4, byteorder="big")
    data = len(data).to_bytes(2, byteorder="big") + checksum + data
    
    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Give two integers - first number of iterations and second for message length growth")
