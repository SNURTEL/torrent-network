#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>

#include "networking/networking.h"
#include "datagrams/datagram.h"

#define SERVERPORT "8080"    // the port users will be connecting to

int main(int argc, char *argv[])
{
    int sockfd;
    struct socketInfo socketInfo;

    if (argc != 3) {
        fprintf(stderr,"usage: hostname message\n");
        exit(1);
    }

    char* datagram = generateDatagram(argv[2], strlen(argv[2]));

    socketInfo = getSocket(false, SERVERPORT, argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    if (sendto(socketInfo.sockfd, datagram, strlen(argv[2]), 0,
               socketInfo.addrinfo->ai_addr, socketInfo.addrinfo->ai_addrlen) == -1)
    {
        printf("sendto: ERROR\n");
        return -1;
    }
    else
    {
        printf("Sent a message!\n");
    }

    free(datagram);
    close(socketInfo.sockfd);
    //freeaddrinfo(socketInfo.addrinfo);

    return 0;
}
