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

    if (argc != 3) {
        fprintf(stderr,"usage: hostname message\n");
        exit(1);
    }

    socketInfo = getSocket(false, SERVERPORT, argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    if (sendMessage(socketInfo, argv[2]) == -1)
        printf("An error has occured, shutting down...\n");
    //else
    //    receiveMessage(socketInfo);

    close(socketInfo.sockfd);
    //freeaddrinfo(socketInfo.addrinfo);

    return 0;
}
