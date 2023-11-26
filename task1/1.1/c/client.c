#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include "networking/networking.h"

#define SERVERPORT "8080"    // the port users will be connecting to

int main(int argc, char *argv[])
{
    int sockfd;
    struct addrinfo hints, *addrinfo;

    if (argc != 3) {
        fprintf(stderr,"usage: talker hostname message\n");
        exit(1);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET; // set to AF_INET to use IPv4
    hints.ai_socktype = SOCK_DGRAM;

    if (getaddrinfo(NULL, SERVERPORT, &hints, &addrinfo) != 0)
    {
        printf("getaddrinfo ERROR");
        return -1;
    }

    sockfd = loopThroughSockets(addrinfo, true);

    if (sockfd == -1)
    {
        printf("Failed to create socket, shutting down...");
        return -1;
    }


    freeaddrinfo(addrinfo);

    close(sockfd);

    return 0;
}
