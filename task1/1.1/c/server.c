#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8080"

int main()
{
    struct socketInfo socketInfo;
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize;
    char buffer[DATAGRAM_SIZE];
    int returnCode;

    socketInfo = getSocket(true, SERVERPORT, NULL);
    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    printf("waiting for a message on port %s\n", SERVERPORT);

    incomingConnSize = sizeof(incomingConn);

    if (recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0,
                 (struct sockaddr *)&incomingConn, &incomingConnSize) == -1)
    {
        printf("recvfrom: ERROR\n");
        return -1;
    }

    char* message = decodeDatagram(buffer);
    if (isBufferEmpty(message, strlen(message)))
        returnCode = -2;
    else
    {
        returnCode = 0;
        printf("Message: %s\n", message);
    }

    char *datagram = generateDatagram("OK", 3);

    sendto(socketInfo.sockfd, datagram, strlen("OK") + 1 + HEADER_SIZE, 0,
           (struct sockaddr *)&incomingConn, incomingConnSize);

    printf("Sent confirmation!\n");


    close(socketInfo.sockfd);
    //freeaddrinfo(socketInfo.addrinfo);

    return returnCode;
}
