#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8081"

int main()
{
    struct socketInfo socketInfo;
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize = sizeof(incomingConn);
    char buffer[DATAGRAM_SIZE];
    char *datagram;

    socketInfo = getSocket(true, SERVERPORT, NULL);
    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    printf("waiting for a message on port %s...\n", SERVERPORT);

    if (recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0,
                 (struct sockaddr *)&incomingConn, &incomingConnSize) == -1)
    {
        printf("recvfrom: ERROR\n");
        close(socketInfo.sockfd);
        return -1;
    }

    char* message = decodeDatagram(buffer);
    if (isBufferEmpty(message, strlen(message)))
    {
        free(message);
        close(socketInfo.sockfd);
        return -1;
    }

    printf("Message: %s\n", message);
    free(message);
    datagram = generateDatagram("OK", 3);

    if (isBufferEmpty(datagram, DATAGRAM_SIZE))
    {
        close(socketInfo.sockfd);
        free(datagram);
        return -1;
    }

    if (sendto(socketInfo.sockfd, datagram, DATAGRAM_SIZE, 0,
           (struct sockaddr *)&incomingConn, incomingConnSize) == -1)
    {
        printf("sendto: ERROR\n");
        close(socketInfo.sockfd);
        free(datagram);
        return -1;
    }

    printf("Sent confirmation!\n");

    close(socketInfo.sockfd);
    free(datagram);

    return 0;
}
