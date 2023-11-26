#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include "stdbool.h"

#ifndef PSI_NETWORKING_H
#define PSI_NETWORKING_H

int bindSocket(struct addrinfo *current, int sockfd)
{
    if (bind(sockfd, current->ai_addr, current->ai_addrlen) == -1) {
        close(sockfd);
        printf("bind socket: ERROR");
        return -1;
    }
    else
        return 0;
}


int loopThroughSockets(struct addrinfo *servinfo, bool isServer)
{
    struct addrinfo *current;
    int sockfd;

    for(current = servinfo; current != NULL; current = current->ai_next) {
        sockfd = socket(current->ai_family, current->ai_socktype,current->ai_protocol);

        if (sockfd == -1)
        {
            printf("create socket: ERROR");
            continue;
        }

        if (isServer)
        {
            if (bindSocket(current, sockfd) == -1)
                continue;
        }

        break;
    }

    return sockfd;
}

#endif //PSI_NETWORKING_H