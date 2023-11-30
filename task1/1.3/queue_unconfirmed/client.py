import socket
import sys
import time
from zlib import adler32 as a32

SERVER_HOST = "z33_server_py"
SERVER_PORT = 8080


def main(message = None):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setblocking(False)

    queue = []

    seq_no = 0

    while True:
        try:
            while True:
                response, addr = client_socket.recvfrom(1024) 
                print(f"Received #{response[0]} {response[1:].decode()} from {addr[0]}:{addr[1]}")
                received_seq_no = response[0]

                to_delete = [i for i, t in enumerate(queue) if t[0] == received_seq_no]
                if to_delete:
                    del queue[to_delete[0]]
        except BlockingIOError:
            pass


        queue.append((seq_no, time.time() - 5))
        for seq in [i[0] for i in queue if i[1] + 5 < time.time()]:
            if message is not None:
                data = bytearray((ord(letter) for letter in message + '\0'))
            else:
                data_length = 10  # excl. header
                data = bytearray([i % 26 + 65 for i in range(data_length - 1)])  # Generate payload
                data.append(ord('\0'))

            checksum = a32(data).to_bytes(4, byteorder="big")
            # Build header
            # Message format: 1B seq_no + 2B lenght + 4B checksum + message
            data = seq.to_bytes(1, byteorder="big") + len(data).to_bytes(2, byteorder="big") + checksum + data
            print(f"{'Send' if seq == seq_no else 'RETRANSMISSION'} #{seq}: {data[:8]}[...] to server")
            client_socket.sendto(data, (SERVER_HOST, SERVER_PORT)) 


        time.sleep(1)

        seq_no = (seq_no + 1) % 256


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
