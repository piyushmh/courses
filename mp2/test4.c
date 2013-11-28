#include <stdio.h>
#include "malloc.h"

#define NUM_MALLOCS 11

int main() {
    int i;
    int* ptrs[NUM_MALLOCS];
    size_t requests[] = {120, 6, 776, 112, 952, 216, 432, 104, 88, 120, 168};
    for (i = 0; i < NUM_MALLOCS; i++) {
        ptrs[i] = (int*) malloc( requests[i]);
    }


    for (i = 0; i < NUM_MALLOCS; i++) {
        free(ptrs[i]);
    }

    return 0;
}
