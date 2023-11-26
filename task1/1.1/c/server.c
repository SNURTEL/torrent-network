#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8080"
#define BACKLOG 10

int main()
{
    struct socketInfo socketInfo;
    char message[2] = "OK";

    socketInfo = getSocket(true, SERVERPORT, NULL);
    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    if (receiveMessage(socketInfo) == -2)
        printf("An error has occured, shutting down...\n");
    //else
    //    sendMessage(socketInfo, message);

    close(socketInfo.sockfd);
    //freeaddrinfo(socketInfo.addrinfo);

    return 0;
}
