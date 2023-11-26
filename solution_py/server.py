import socket


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
            server_socket.sendto(response, addr)  # Odsyłanie odpowiedzi do klienta
            print(f"Odebrano poprawne dane od {addr}")
        else:
            print(f"Odebrano niepoprawne dane od {addr}")


def verify_data(data):
    # Weryfikacja długości datagramu i zawartości
    if len(data) >= 2 and data[:2] == len(data[2:]).to_bytes(2, byteorder="big"):
        # print(data)
        return True
    return False


if __name__ == "__main__":
    main()
