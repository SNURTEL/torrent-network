#include <malloc.h>

#include "../binaryUtil/binaryUtil.h"

#ifndef PSI_DATAGRAM_H
#define PSI_DATAGRAM_H

const int DATAGRAM_SIZE = 1024; // in bytes
const int HEADER_SIZE = 6;
const uint32_t MOD_ADLER = 65521;

uint32_t adler32(unsigned const char *buffer, const size_t len)
{
    uint32_t a = 1, b = 0;
    size_t index;

    for (index = 0; index < len; ++index)
    {
        a = (a + buffer[index]) % MOD_ADLER;
        b = (b + a) % MOD_ADLER;
    }

    return (b << 16) | a;
}

char* generateDatagram(const unsigned char* message, const short messageLength)
{
    unsigned char* datagram = (unsigned char *)malloc(DATAGRAM_SIZE);

    memset(datagram, 0, DATAGRAM_SIZE);

    if (messageLength > DATAGRAM_SIZE - HEADER_SIZE)
    {
        printf("%s", "ERROR: message is too long");
        return datagram;
    }

    unsigned char* binarySize = shortToBinary(messageLength);

    for (int i = 0; i < 8; ++i)
        datagram[0] = bit_set_to(datagram[0], 7 - i, (bool)binarySize[i]);

    for (int i = 8; i < 16; ++i)
        datagram[1] = bit_set_to(datagram[1], 15 - i, (bool)binarySize[i]);

    // encode checksum in datagram
    uint32_t checksum = adler32(message, messageLength);
    datagram[2] = (checksum >> 24) & 0xFF;
    datagram[3] = (checksum >> 16) & 0xFF;
    datagram[4] = (checksum >> 8) & 0xFF;
    datagram[5] = checksum & 0xFF;

    for (int i = 0; i < messageLength - 1; ++i)
        datagram[i+HEADER_SIZE] = message[i];

    free(binarySize);

    return datagram;
}

unsigned char* decodeDatagram(const unsigned char* datagram)
{
    unsigned char size[16];

    for (int i = 0; i < 8; ++i)
        size[i] = bit_check(datagram[0], 7 - i);
    for (int i = 8; i < 16; ++i)
        size[i] = bit_check(datagram[1], 15 - i);

    unsigned short messageLength = binaryToShort(size);

    unsigned char* message = (unsigned char *)malloc(messageLength);

    for (int i = 0; i < messageLength; ++i)
        message[i] = datagram[i+HEADER_SIZE];

    uint32_t theirChecksum = ((uint32_t)datagram[2] << 24) | ((uint32_t)datagram[3] << 16) | ((uint32_t)datagram[4] << 8) | (uint32_t)datagram[5];
    uint32_t ourChecksum = adler32(message, messageLength);

    if (theirChecksum != ourChecksum)
    {
        printf("Checksum is not valid!\n");
        memset(message, 0, messageLength);
    }

    return message;
}

#endif //PSI_DATAGRAM_H
