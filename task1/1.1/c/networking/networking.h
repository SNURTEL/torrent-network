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

#define BACKLOG 10

struct socketInfo
{
    int sockfd;
    struct addrinfo *addrinfo;
};

int bindSocket(struct addrinfo *current, int sockfd)
{
    if (bind(sockfd, current->ai_addr, current->ai_addrlen) == -1) {
        close(sockfd);
        printf("bind socket: ERROR\n");
        return -1;
    }
    else
        return 0;
}


struct socketInfo loopThroughSockets(struct addrinfo *servinfo, bool isServer)
{
    struct addrinfo *current;
    struct socketInfo socketInfo;
    int sockfd;

    for(current = servinfo; current != NULL; current = current->ai_next) {
        sockfd = socket(current->ai_family, current->ai_socktype,current->ai_protocol);

        if (sockfd == -1)
        {
            printf("create socket: ERROR\n");
            continue;
        }

        if (isServer)
        {
            if (bindSocket(current, sockfd) == -1)
                continue;
        }

        break;
    }

    socketInfo.sockfd = sockfd;
    socketInfo.addrinfo = current;
    return socketInfo;
}

struct socketInfo getSocket(bool isServer, const char* port, const char* hostname)
{
    struct addrinfo hints, *addrinfo;
    struct socketInfo socketInfo;

    socketInfo.sockfd = -1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;

    if (isServer)
        hints.ai_flags = AI_PASSIVE; // use my IP

    if (getaddrinfo(hostname, port, &hints, &addrinfo) != 0)
    {
        printf("getaddrinfo ERROR\n");
        return socketInfo;
    }

    socketInfo = loopThroughSockets(addrinfo, isServer);
    freeaddrinfo(addrinfo);

    return socketInfo;
}

int sendMessage(struct socketInfo socketInfo, char* message)
{
    char* datagram = generateDatagram(message, strlen(message) + 1);
    int returnCode;

    if (sendto(socketInfo.sockfd, datagram, strlen(message) + HEADER_SIZE, 0,
               socketInfo.addrinfo->ai_addr, socketInfo.addrinfo->ai_addrlen) == -1)
    {
        printf("sendto: ERROR\n");
        returnCode = -1;
    }
    else
    {
        printf("Sent a message!\n");
        returnCode = 0;
    }

    free(datagram);
    return returnCode;
}

int receiveMessage(struct socketInfo socketInfo)
{
    struct sockaddr_storage incomingConn;
    socklen_t incomingConnSize;
    char buffer[DATAGRAM_SIZE];
    int returnCode;

    listen(socketInfo.sockfd, BACKLOG);
    printf("waiting for a message...\n");

    incomingConnSize = sizeof(incomingConn);

    if (recvfrom(socketInfo.sockfd, buffer, DATAGRAM_SIZE, 0,
                 (struct sockaddr *)&incomingConn, &incomingConnSize) == -1)
    {
        printf("recvfrom: ERROR\n");
        return -1;
    }

    char* message = decodeDatagram(buffer);
    if (isBufferEmpty(message, strlen(message)))
        returnCode = -2;
    else
    {
        returnCode = 0;
        printf("Message: %s\n", message);
    }

    free(message);
    return returnCode;
}

#endif //PSI_NETWORKING_H