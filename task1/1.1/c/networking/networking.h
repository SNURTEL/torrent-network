#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include "stdbool.h"
#include "../datagrams/datagram.h"

#ifndef PSI_NETWORKING_H
#define PSI_NETWORKING_H

struct socketInfo
{
    int sockfd;
    struct addrinfo *addrinfo;
};

int bindSocket(struct addrinfo *current, int sockfd)
{
    if (bind(sockfd, current->ai_addr, current->ai_addrlen) == -1) {
        close(sockfd);
        return -1;
    }
    else
        return 0;
}


struct socketInfo loopThroughAddrinfos(struct addrinfo *servinfo, const bool isServer)
{
    struct addrinfo *current;
    struct socketInfo socketInfo;
    int sockfd = -1;
    bool wasBindSuccessful = false;

    for(current = servinfo; current != NULL; current = current->ai_next) {
        sockfd = socket(current->ai_family, current->ai_socktype,current->ai_protocol);

        if (sockfd == -1)
        {
            continue;
        }

        if (isServer)
        {
            if (bindSocket(current, sockfd) == -1)
            {
                wasBindSuccessful = false;
                continue;
            }
            else
                wasBindSuccessful = true;

        }
        break;
    }

    if (sockfd == -1)
        printf("create socket: ERROR\n");
    if (!wasBindSuccessful && isServer)
        printf("bind socket: ERROR\n");

    socketInfo.sockfd = sockfd;
    socketInfo.addrinfo = current;
    return socketInfo;
}

struct socketInfo getSocket(const bool isServer, const char* port, const char* hostname)
{
    struct addrinfo hints, *addrinfo;
    struct socketInfo socketInfo;

    socketInfo.sockfd = -1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;

    if (isServer)
        hints.ai_flags = AI_PASSIVE;

    if (getaddrinfo(hostname, port, &hints, &addrinfo) != 0)
    {
        printf("getaddrinfo: ERROR\n");
        freeaddrinfo(addrinfo);
        return socketInfo;
    }

    socketInfo = loopThroughAddrinfos(addrinfo, isServer);
    freeaddrinfo(addrinfo);

    return socketInfo;
}

#endif //PSI_NETWORKING_H