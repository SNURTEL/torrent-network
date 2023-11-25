#include <malloc.h>

#include "../binaryUtil/binaryUtil.h"

#ifndef PSI_DATAGRAM_H
#define PSI_DATAGRAM_H

int DATAGRAM_SIZE = 1024; // in bytes
int HEADER_SIZE = 2;

char* generateDatagram(const char* message, const short messageLength)
{
    char* datagram = (char *)malloc(DATAGRAM_SIZE);

    for (int i = 0; i < DATAGRAM_SIZE; ++i)
        datagram[i] = 0;

    if (messageLength > DATAGRAM_SIZE - HEADER_SIZE)
    {
        printf("%s", "ERROR: message is too long");
        return datagram;
    }

    char* binarySize = shortToBinary(messageLength);

    for (int i = 0; i < 8; ++i)
        datagram[0] = bit_set_to(datagram[0], 7 - i, (bool)binarySize[i]);

    for (int i = 8; i < 16; ++i)
        datagram[1] = bit_set_to(datagram[1], 15 - i, (bool)binarySize[i]);

    for (int i = 0; i < messageLength; ++i)
        datagram[i+2] = message[i];

    return datagram;
}



char* decodeDatagram(char* datagram)
{
    char size[16];

    for (int i = 0; i < 8; ++i)
        size[i] = bit_check(datagram[0], 7 - i);
    for (int i = 8; i < 16; ++i)
        size[i] = bit_check(datagram[1], 15 - i);

    unsigned short messageLength = binaryToShort(size);

    char* message = (char *)malloc(messageLength);

    for (int i = 0; i < messageLength; ++i)
        message[i] = datagram[i+2];

    return message;
}

#endif //PSI_DATAGRAM_H
