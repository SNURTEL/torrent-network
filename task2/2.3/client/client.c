#include <stdio.h>
#include <byteswap.h>
#include <string.h>

#include "networking/networking.h"
#include "data/linked_list.h"

void print_node(node curnode)
{
    printf("dynamic: %s\n", curnode.dynamic_string);
}

int main(int argc, char *argv[])
{
    printf("id: %lu\n\n", sizeof(node));
    printf("id: %lu\n\t", sizeof(struct node*));
    printf("id: %lu\n\t", sizeof(uint16_t));
    printf("id: %lu\n\t", sizeof(uint32_t));
    printf("id: %lu\n\t", sizeof(char[6]));
    printf("id: %lu\n\t", sizeof(uint32_t));

    struct socketInfo socketInfo;
    uint32_t list_length = 5;
    node* linked_list = create_linked_list(list_length);

    if (argc != 3) {
        printf("usage: hostname port\n");
        return 0;
    }

    printf("%s %s", argv[1], argv[2]);

    socketInfo = getSocket(argv[2], argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    printf("Connected to server, sending data...\n");

    uint32_t buf[1];
    __bswap_32(list_length); // convert to big endian
    buf[0] = list_length;

    if (send(socketInfo.sockfd, buf, sizeof(uint32_t), 0) != -1)
        printf("Sent list length!\n");
    else
    {
        printf("Error in sending list length, shutting down...\n");
        return -1;
    }

    node* current_node = linked_list;
    int i = 0;

    while (current_node != NULL)
    {
        printf("dynamic: %s\n", current_node->dynamic_string);
        printf("id: %d, short_val: %d, int_val: %d, fixed_string: %s, dynamic_string: %s \n",
               i, current_node->short_val, current_node->int_val, current_node->fixed_string, current_node->dynamic_string);

        if (send(socketInfo.sockfd, current_node,
                 sizeof(node)+ current_node->dynamic_string_length, 0) != -1)
        {
            printf("Sent node of id %d\n", i);
        }
        else
        {
            printf("Error in sending node, shutting down...\n");
            return -1;
        }
        current_node = current_node->next;
        i++;
    }

    printf("Sent the linked list!\n");

    return 0;
}

