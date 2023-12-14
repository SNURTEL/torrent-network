#include <stdio.h>
#include "string.h"

#include "networking/networking.h"
#include "data/linked_list.h"

int main(int argc, char *argv[])
{
    struct socketInfo socketInfo;
    uint32_t list_length = 5;
    node* linked_list = create_linked_list(list_length);

    if (argc != 3) {
        printf("usage: hostname port\n");
        return 0;
    }

    socketInfo = getSocket(argv[2], argv[1]);

    if (socketInfo.sockfd == -1)
    {
        printf("Failed to create socket, shutting down...\n");
        return -1;
    }

    printf("Connected to server, sending data...");

    uint32_t buf[1];
    buf[0] = list_length;

    if (send(socketInfo.sockfd, buf, sizeof(uint32_t), 0) != -1)
        printf("Sent list length!");
    else
    {
        printf("Error in sending list length, shutting down...\n");
        return -1;
    }

    node* current_node = linked_list;
    node n_buf[1];
    int i = 0;

    while (current_node != NULL)
    {
        n_buf[0] = *current_node;

        if (send(socketInfo.sockfd, n_buf,
                 sizeof(node) + current_node->dynamic_string_length, 0) != -1)
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