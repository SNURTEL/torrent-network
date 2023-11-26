#include <string.h>
#include <stdint-gcc.h>
#include "stdio.h"

#include "datagrams/datagram.h"

int main()
{
    /*char* datagram = generateDatagram("elkowicze", 3);
    char* message = decodeDatagram(datagram);

    printf("%s", message);

    free(datagram);
    free(message);*/
    unsigned char datagram[5];
    char text[] = "123456789";
    uint32_t n = adler32(text, 10);
    datagram[0] = 123;
    datagram[1] = (n >> 24) & 0xFF;
    datagram[2] = (n >> 16) & 0xFF;
    datagram[3] = (n >> 8) & 0xFF;
    datagram[4] = n & 0xFF;

    uint32_t theirChecksum = ((uint32_t)datagram[1] << 24) | ((uint32_t)datagram[2] << 16) | ((uint32_t)datagram[3] << 8) | (uint32_t)datagram[4];

    printf("%d\n", n);
    printf("%d\n", theirChecksum);
    return 0;
}