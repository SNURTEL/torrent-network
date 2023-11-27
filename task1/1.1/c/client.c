#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8080"

int main(int argc, char *argv[])
{
    struct socketInfo socketInfo;
    char buffer[DATAGRAM_SIZE];
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize;
    int returnCode;

    if (argc != 3) {
        fprintf(stderr,"usage: hostname message\n");
        exit(1);
    }

    char* datagram = generateDatagram(argv[2], strlen(argv[2]) + 1);

    socketInfo = getSocket(false, SERVERPORT, argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    if (sendto(socketInfo.sockfd, datagram, strlen(argv[2]) + 1 + HEADER_SIZE , 0,
               socketInfo.addrinfo->ai_addr, socketInfo.addrinfo->ai_addrlen) == -1)
    {
        printf("sendto: ERROR\n");
        returnCode = -1;
    }
    else
    {
        printf("Sent a message!\n");
        returnCode = 0;
    }

    printf("Waiting for confirmation...\n");
    incomingConnSize = sizeof(incomingConn);
    recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0, (struct sockaddr *)&incomingConn, &incomingConnSize);
    char* message = decodeDatagram(buffer);

    printf("Confirmation: %s\n", message);

    close(socketInfo.sockfd);
    free(datagram);
    return returnCode;
    //freeaddrinfo(socketInfo.addrinfo);
}
