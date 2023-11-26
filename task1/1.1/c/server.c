#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8080"
#define BACKLOG 10
#define DATAGRAM_SIZE 1024

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main()
{
    char buffer[DATAGRAM_SIZE];
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize;
    struct socketInfo socketInfo;

    socketInfo = getSocket(true, SERVERPORT, NULL);
    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...");
        return -1;
    }
    listen(socketInfo.sockfd, BACKLOG);
    printf("listener: waiting to recvfrom...\n");

    incomingConnSize = sizeof(incomingConn);

    if (recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0,
                 (struct sockaddr *)&incomingConn, &incomingConnSize) == -1)
    {
        printf("recvfrom: ERROR");
        return -1;
    }

    char* message = decodeDatagram(buffer);
    printf("Message: %s", message);

    free(message);
    close(socketInfo.sockfd);
    //freeaddrinfo(socketInfo.addrinfo);

    return 0;
}
