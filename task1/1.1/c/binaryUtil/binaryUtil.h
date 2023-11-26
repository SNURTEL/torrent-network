#include <malloc.h>
#include "stdbool.h"
#include <math.h>
#ifndef PSI_BINARYUTIL_H
#define PSI_BINARYUTIL_H

int isBufferEmpty(char * buffer, int size)
{
    for(int i = 0; i < size; i++) {
        if (buffer[i] != 0)
            return 0;
    }
    return 1;
}

char* shortToBinary(unsigned short n)
{
    char* binary = (char *)malloc(16);
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

unsigned short binaryToShort(char* binary)
{
    short n = 0;
    for (int i = 0; i < 16; ++i)
        n += binary[i] * pow(2, 16 - 1 - i);
    return n;
}

char bit_set_to(char number, char n, bool x) {
    return (number & ~((char)1 << n)) | ((char)x << n);
}

bool bit_check(char number, char n) {
    return (number >> n) & (char)1;
}

#endif //PSI_BINARYUTIL_H
