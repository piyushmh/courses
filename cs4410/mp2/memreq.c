#include "memreq.h"

#include <stddef.h>
#include <stdint.h>
#include <unistd.h>

char* get_memory(unsigned num_bytes) {
    char *page = (char*)sbrk((intptr_t) num_bytes); //revert me to original

    return (page != (char*) -1 ? page : NULL);
}

