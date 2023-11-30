import socket
import sys
import time
from zlib import adler32 as a32

SERVER_HOST = "z33_server_py"
SERVER_PORT = 8080


def main(message = None):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3.0)

    while True:
        if message is not None:
            data = bytearray((ord(letter) for letter in message + '\0'))
        else:
            data_length = 10  # excl. header
            data = bytearray([i % 26 + 65 for i in range(data_length - 1)])  # Generate payload
            data.append(ord('\0'))

        checksum = a32(data).to_bytes(4, byteorder="big")
        # Build header
        # Message format: 2B lenght + 4B checksum + message
        data = len(data).to_bytes(2, byteorder="big") + checksum + data
        response = None
        while not response:
            try:
                print(f"Send {data[:8]}[...] to server")
                client_socket.sendto(data, (SERVER_HOST, SERVER_PORT)) 
                response, addr = client_socket.recvfrom(1024) 
                print(f"Received {response.decode()} from {addr[0]}:{addr[1]}")
            except TimeoutError:
                print("Timeout!")
                continue

        time.sleep(1)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
