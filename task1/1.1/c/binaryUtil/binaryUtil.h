#include <malloc.h>
#include "stdbool.h"
#include <math.h>
#ifndef PSI_BINARYUTIL_H
#define PSI_BINARYUTIL_H

int isBufferEmpty(const char * buffer, const int size)
{
    for(int i = 0; i < size; i++) {
        if (buffer[i] != 0)
            return 0;
    }
    return 1;
}

unsigned char* shortToBinary(unsigned short n)
{
    unsigned char* binary = (unsigned char *)malloc(16);
    memset(binary, 0, 16);
    int i = sizeof(n) * 8 - 1;
    while (n != 0)
    {
        binary[i] = n % 2;
        n = n / 2;
        --i;
    }

    return binary;
}

unsigned short binaryToShort(const unsigned char* binary)
{
    short n = 0;
    for (int i = 0; i < 16; ++i)
        n += binary[i] * pow(2, 16 - 1 - i);
    return n;
}

unsigned char bit_set_to(const unsigned char number, const unsigned char n, const bool x) {
    return (number & ~((unsigned char)1 << n)) | ((unsigned char)x << n);
}

bool bit_check(const unsigned char number, const unsigned char n) {
    return (number >> n) & (unsigned char)1;
}

#endif //PSI_BINARYUTIL_H
