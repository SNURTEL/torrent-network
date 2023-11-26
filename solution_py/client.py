import socket
import sys

def main():
    server_ip = "127.0.0.1"
    server_port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if len(sys.argv) > 1:
        # Take the message from the command line arguments
        msg = sys.argv[1]
        data = bytearray((ord(letter) for letter in msg + "\0"))
    else:
        data_length = 10  # Długość danych bez uwzględnienia nagłówka
        data = bytearray([i % 26 + 65 for i in range(data_length - 1)])  # Generowanie danych A-Z
        data.append(ord("\0"))

    # Dodanie nagłówka z informacją o długości
    data = len(data).to_bytes(2, byteorder="big") + data

    client_socket.sendto(data, (server_ip, server_port))  # Wysyłanie danych do serwera

    response, addr = client_socket.recvfrom(1024)  # Odbieranie odpowiedzi od serwera
    print(f"Odpowiedź od serwera: {response.decode()}")

if __name__ == "__main__":
    main()
