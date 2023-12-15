#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <errno.h>
#include "stdbool.h"

#ifndef PSI_NETWORKING_H
#define PSI_NETWORKING_H

struct socketInfo
{
    int sockfd;
    struct addrinfo *addrinfo;
};


struct socketInfo loopThroughAddrinfos(struct addrinfo *servinfo)
{
    struct addrinfo *current;
    struct socketInfo socketInfo;
    int sockfd = -1;
    bool isConnected = false;

    for(current = servinfo; current != NULL; current = current->ai_next) {
        sockfd = socket(current->ai_family, current->ai_socktype,current->ai_protocol);

        if (sockfd == -1)
        {
            continue;
        }

        if (connect(sockfd, current->ai_addr, current->ai_addrlen) == -1)
        {
            isConnected = false;
            continue;
        }
        else
            isConnected = true;

        break;
    }

    if (sockfd == -1)
        printf("create socket: ERROR\n");
    if (!isConnected) {
        printf("connect socket: ERROR\n");
        printf("%d", errno);
    }

    socketInfo.sockfd = sockfd;
    socketInfo.addrinfo = current;
    return socketInfo;
}

struct socketInfo getSocket(const char* port, const char* hostname)
{
    struct addrinfo hints, *addrinfo;
    struct socketInfo socketInfo;

    socketInfo.sockfd = -1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(hostname, port, &hints, &addrinfo) != 0)
    {
        printf("getaddrinfo: ERROR\n");
        printf("%d\n", errno);
        freeaddrinfo(addrinfo);
        return socketInfo;
    }

    socketInfo = loopThroughAddrinfos(addrinfo);
    freeaddrinfo(addrinfo);

    return socketInfo;
}

#endif //PSI_NETWORKING_H