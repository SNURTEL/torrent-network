#ifndef C_LINKED_LIST_H
#define C_LINKED_LIST_H

#include <stdint.h>
#include <stdlib.h>
#include "string.h"
#include "stdio.h"


typedef struct node
{
    struct node* next;
    uint16_t short_val;
    uint32_t int_val;
    char fixed_string[4];
    uint32_t dynamic_string_length;
    char dynamic_string[];
} node;


node* create_node(uint16_t short_val, uint32_t int_val, char* fixed_message, char* dynamic_message)
{
    uint32_t dynamic_message_length = strlen(dynamic_message);
    node *new_node = malloc(sizeof(*new_node) + dynamic_message_length);

    new_node->next = NULL;
    new_node->short_val = short_val;
    new_node->int_val = int_val;
    strncpy(new_node->fixed_string, fixed_message, 4);
    strncpy(new_node->dynamic_string, dynamic_message, dynamic_message_length);
    new_node->dynamic_string_length = dynamic_message_length;

    return new_node;
}

char* create_message(uint32_t message_length)
{
    char* message = malloc(sizeof(char) * (message_length + 1));

    for (int i = 0; i < message_length; i++)
        message[i] = 'a';
    message[message_length] = 0;

    return message;
}

node* create_linked_list(uint32_t list_length)
{
    node* current_node = NULL;
    node* prev_node = NULL;
    node* parent_node = NULL;

    for (int i = 0; i < list_length; ++i)
    {
        current_node = create_node(i, i * 2, "abc", create_message(i+1));

        if (i == 0)
            parent_node = current_node;

        if (i != 0)
            prev_node->next = current_node;

        prev_node = current_node;
    }

    return parent_node;
}

void print_linked_list(node* parent_node)
{
    node* current_node = parent_node;
    int i = 1;

    while (current_node != NULL)
    {
        printf("id: %d, short_val: %d, int_val: %d, fixed_string: %s, dynamic_string: %s \n",
               i, current_node->short_val, current_node->int_val, current_node->fixed_string, current_node->dynamic_string);

        current_node = current_node->next;
        i++;
    }
}

#endif //C_LINKED_LIST_H