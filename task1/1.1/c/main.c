#include "stdio.h"

#include "datagrams/datagram.h"

int main()
{
    char* datagram = generateDatagram("elkowicze", 3);
    char* message = decodeDatagram(datagram);

    printf("%s", message);
    return 0;
}