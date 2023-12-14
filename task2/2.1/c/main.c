#include "data/linked_list.h"

int main()
{
    //node* linked_list = create_linked_list(10);
    //print_linked_list(linked_list);
    printf("%lu\n", sizeof(node*) + sizeof(uint16_t) + sizeof(uint32_t) + sizeof(char[6]) + sizeof(uint32_t));
    printf("%lu\n", sizeof(node));
}
