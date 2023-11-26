#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "networking/networking.h"

#define MYPORT "8080"
#define MAXBUFLEN 100

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
    int sockfd;
    struct addrinfo hints, *addrinfo;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET6; // set to AF_INET to use IPv4
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_flags = AI_PASSIVE; // use my IP

    if (getaddrinfo(NULL, MYPORT, &hints, &addrinfo) != 0)
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

    printf("listener: waiting to recvfrom...\n");


    close(sockfd);

    return 0;
}
