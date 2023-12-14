#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

int main(int argc, char *argv[])
{
    struct socketInfo socketInfo;
    char buffer[DATAGRAM_SIZE];
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize = sizeof(incomingConn);
    char* datagram;

    if (argc != 4) {
        printf("usage: hostname message port\n");
        return 0;
    }

    socketInfo = getSocket(false, argv[3], argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    datagram = generateDatagram(argv[2], strlen(argv[2]) + 1);

    if (isBufferEmpty(datagram, DATAGRAM_SIZE))
    {
        close(socketInfo.sockfd);
        free(datagram);
        return -1;
    }

    //strlen(argv[2]) + 1 + HEADER_SIZE
    if (sendto(socketInfo.sockfd, datagram, DATAGRAM_SIZE , 0,
               socketInfo.addrinfo->ai_addr, socketInfo.addrinfo->ai_addrlen) == -1)
    {
        printf("sendto: ERROR\n");
        close(socketInfo.sockfd);
        free(datagram);
        return -1;
    }

    printf("Sent a message!\n");

    printf("Waiting for confirmation...\n");

    if (recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0,
                 (struct sockaddr *)&incomingConn, &incomingConnSize) == -1)
    {
        printf("No confirmation received, shutting down...\n");
        close(socketInfo.sockfd);
        free(datagram);
        return -1;
    }

    char* message = decodeDatagram(buffer);

    if (isBufferEmpty(message, strlen(message) + 1))
    {
        printf("Checksum is invalid!\n");
        close(socketInfo.sockfd);
        free(datagram);
        free(message);
        return -1;
    }

    printf("Confirmation: %s\n", message);
    close(socketInfo.sockfd);
    free(datagram);
    free(message);
    return 0;
}
