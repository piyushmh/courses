/* MP2
   author - piyush
*/

#include <errno.h>
#include <limits.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#include "malloc.h"
#include "memreq.h"

#define ALIGNMENT 16 
#define SHIFT 4
#define align(size)                 ((((size-1)>>SHIFT)<<SHIFT)+ALIGNMENT)
#define BOUNDARYSIZE                (sizeof(struct s_boundary))
#define GETSIZE(size)               (size & -2)
#define GETFREEBIT(block)           ((block->size)&1)
#define SETUSED(size)               (size & ~(1))
#define NEXTPTR(node)               ((boundary*)(node+1))
#define PREVPTR(node)               ((boundary*)(((size_t*)(node+1)+1)))
#define GETFOOTERFROMHEADER(block)  ((boundary)((char*)(block+1) + GETSIZE(block->size)))


/* Structure used to define both header and footer */
typedef struct s_boundary{
    size_t size;
}* boundary;

#define NBUCKETS 7
#define MIN_MEMORY_BLOCK 1024
static boundary memory_buckets[7] = {NULL,NULL,NULL,NULL,NULL,NULL,NULL};
static char* heap_head = NULL; //This defines the start of heap
size_t  heap_size = 0; //This defines the end of heap

static char temp[256];
//static int nmalloc = 0;
//static int nfree = 0;

//#define DEBUG

void pps(char *t){
   while(*t)
    putchar(*(t++));
}

int find_memory_bin(size_t size){
    
    if      (size > 512)    return 6;
    else if (size > 256)    return 5;
    else if (size > 128)    return 4;
    else if (size > 64)     return 3;
    else if (size > 32)     return 2;
    else if (size > 16)     return 1;
    else                    return 0;
}


void printBlock(boundary h){
    #ifdef DEBUG
        sprintf(temp,"Header addr :%p\t", h); pps(temp);
        sprintf(temp,"Header size :%lu\t", GETSIZE(h->size)); pps(temp);
        if(GETFREEBIT(h) == 1){
            sprintf(temp, "Bucket num :%d\t", find_memory_bin(GETSIZE(h->size)));   pps(temp);
            sprintf(temp, "Node is Free\t");   pps(temp);
            sprintf(temp,"Next free pointer :%p\t", *NEXTPTR(h)); pps(temp);
            sprintf(temp,"Prev free pointer :%p\t", *PREVPTR(h)); pps(temp);
        }
        boundary f = (boundary)((char*)(h+1) + GETSIZE(h->size));
        sprintf(temp,"Footer addr :%p\t", f);   pps(temp);
        sprintf(temp,"Footer size :%lu\n", GETSIZE(f->size));    pps(temp);
    #endif
}

void printmemoryblocks(boundary head){
    sprintf(temp,"\nHeap starts :%p\n",heap_head);  pps(temp);
    if(head==NULL){
        sprintf(temp,"Nothing to print, returning");  pps(temp);
        return;
    }
    while(1){
        printBlock(head);
        boundary nextblock = GETFOOTERFROMHEADER(head) + 1;
        if( ( (char*)nextblock  - (heap_size + heap_head)) >= 0 ){
            break;
        }else{
            head = nextblock;
        }
    }
    sprintf(temp,"\nHeap ends :%p\n",heap_head+ heap_size); pps(temp);
}

void dummy(char x){} //dummy method to segfault, assert calls printf internally

int is_memory_within_heap(void* h){
    if( (heap_head - ((char*)h)) > 0){ //before heap starts
        //dummy(*(char *)NULL);
        return 0;  
    }
    if((((char*)h) - (heap_head + heap_size)) > 0){ //after heap ends
        //dummy(*(char *)NULL);
        return 0;
    }
    return 1;
}

/*  Method to test the fidelity of a block  */
int validate_block(boundary h, size_t size, int free){
    
    if( h == NULL) 
        return 1; //hmm, check this later

    if(!is_memory_within_heap(h)){
        //dummy(*(char *)NULL);
        return 0;  
    } 

    boundary f = GETFOOTERFROMHEADER(h);
   
    if(!is_memory_within_heap((char*)f + BOUNDARYSIZE)){
        //dummy(*(char *)NULL);
        return 0;
    }

    if( GETSIZE(h->size) != GETSIZE(f->size)){
        //dummy(*(char *)NULL);
        return 0;
    }

    if( GETFREEBIT(h) == 1){
        boundary* n = NEXTPTR(h);
        boundary* p = PREVPTR(h);
        if((*n) != NULL){
            if(!is_memory_within_heap(*n)){
                //dummy(*(char *)NULL);
                return 0;
            }
        }
        if((*p) != NULL){
            if(!is_memory_within_heap(*p)){
                //dummy(*(char*)NULL);
                return 0;
            }
        }
    }


    if( free!= -1){
        if(((h->size)&1) != free){
            //dummy(*(char*)NULL);
            return 0;
        }
        if(((f->size)&1) != free){
            //dummy(*(char*)NULL);
            return 0;
        }
        if(size!=0){
            if(GETSIZE(h->size) != size){
                //dummy(*(char*)NULL);
                return 0;
            }
            if(GETSIZE(f->size) != size){
                //dummy(*(char*)NULL);
                return 0;
            }
        }    
    }
    
    return 1;
}

/*  Method to check the robustness of the heap  */
void heap_checker(boundary head){
    if(head == NULL)
        return;
    while(1){
        if(!validate_block(head,0,-1)){
            pps("Check failed\n");
            printBlock(head);
            dummy(*(char*)NULL);
        }
        boundary nextblock = GETFOOTERFROMHEADER(head) + 1;

        if( ( (char*)nextblock  - (heap_size + heap_head)) >= 0 ){
            break;
        }else{
            head = nextblock;
        }
    }
    //pps("Checker passed\n");
}

void ll_checker(){
    int i;
    for(i=0;i<NBUCKETS;i++){
        validate_block(memory_buckets[i],0,1);
    }
}

void set_boundary_tags(
    boundary block,
    size_t size,
    int free,
    boundary nextfree,
    boundary prevfree){

    if(free){
        size = size | 1;
        boundary* next = NEXTPTR(block);    *next = nextfree;
        boundary* prev = PREVPTR(block);    *prev = prevfree;
   
    }

    block->size = size;
    block = (boundary)(GETSIZE(size) + (char*)(block+1));//move to footer
    block->size = size;
    return;
}

void print_link_list(boundary head){
    if(head==NULL){
        printf("%s\n", "Empty list, returning");
        return;
    }
    while(head!=NULL){
        printBlock(head);
        head = *NEXTPTR(head);
    }
    return;
}

void addnode(const int bucket_number, boundary node){
    
    boundary head = memory_buckets[bucket_number];
    if(head == NULL){
        head = node;
    }else{
        boundary* nextnode = NEXTPTR(node);
        boundary* prevhead = PREVPTR(head);
        *nextnode = head;
        *prevhead = node;
        head = node;
    }
    validate_block(head, 0, 1);
    validate_block(node, 0, 1);
    memory_buckets[bucket_number] = head;
    return;
}

void delete_from_list(int bucket_number, boundary node){
   
    validate_block(node,0,1);
    //boundary head = memory_buckets[bucket_number];
    boundary *prev = PREVPTR(node);
    boundary *next = NEXTPTR(node);
  
    if((*prev) != NULL){
        boundary* prevnext = NEXTPTR(*prev);
        *prevnext= *next;
        validate_block(*prev, 0, -1);
    }
    if((*next)!=NULL){
        boundary* nextprev = PREVPTR(*next);
        *nextprev = *prev;
        validate_block(*next, 0, 1);
    }
    if((*prev)==NULL){
        //now we need to move the head,this also handles the case when *next is NULL
        memory_buckets[bucket_number] = *next; 
    }

    return;
}

int extend_heap(size_t size){
    
    if(size < MIN_MEMORY_BLOCK)
        size = MIN_MEMORY_BLOCK;
    
    char* page= get_memory(size);
    boundary allocated_block;
    if(heap_head == NULL){ //this will be   true only for the first time malloc is called
        heap_head = page;
    }

    if(page==NULL){//Memory could have exhausted
        errno = ENOMEM;
        return 0;
    }else{
        allocated_block = (boundary)page;
        size -= 2*BOUNDARYSIZE; //remove the header and footer for free block
        set_boundary_tags(allocated_block,size,1, NULL, NULL);
        heap_size += (size + 2*BOUNDARYSIZE); //add header and footer to the heap size
        validate_block(allocated_block,size, 1);
        addnode(NBUCKETS-1,allocated_block);
    }
    return 1;//successful
}

/*Traverse the link list and find block with size greated than sized passed
  and remove the block from the list if found
  Returns null if no appropriate sized block is found   */
boundary traverse_link_list(const int bucket_number, const size_t size){
    
    boundary ret_block = NULL;
    //if the bucket hasn't been initiazed, then start would be null 
    //and the code just falls through
    boundary start = memory_buckets[bucket_number];
  
    while(start!=NULL){      
        if(GETSIZE(start->size) >=size){
            ret_block = start;
            break;
        }else{
            start = *(NEXTPTR(start));
        }
    }
    if(ret_block!=NULL){
        delete_from_list(bucket_number, ret_block);
    }
    return ret_block;
}

/*Returns the first block that fits. Returns null if there 
are no such blocks or the link lists are null*/
boundary find_free_fit(
    int bucket_number,
    size_t size){

    boundary ret_block = NULL;//final block to return
    int i=0;
    for(i=bucket_number;i< NBUCKETS;i++){
        ret_block = traverse_link_list(i, size);
        if(ret_block!=NULL){//this means we found a block, yipee!!
            break;
        }
    }
    return ret_block;
}

int check_if_splittable(boundary block, int size){
    int total_size = GETSIZE(block->size);
    total_size -= size;
    total_size -= 2*BOUNDARYSIZE; //For the new header and footer
    total_size -= 2* sizeof(size_t); //Free block needs 2 pointers as well for LL
    if(total_size > 0)
        return 1;
    else return 0;
}

/*  Break block into used and free, set the size of 
    both blocks and set the free bit for latter     */
void split_block(boundary block, const size_t size){

    int freeblocksize = GETSIZE(block->size) - size - 2*BOUNDARYSIZE;

    //Saving local copies of a variable as these might be overwritten
    // 1.15 hourse spent debuggin', not cool!!
    //boundary nextfree = *(NEXTPTR(block));
    //boundary prevfree = *(PREVPTR(block));
    set_boundary_tags(block, size, 0, NULL,NULL);  
    validate_block(block,size,0);

    boundary freeblock = ((boundary)((char*)(block+1)+ size))+1;
    set_boundary_tags(freeblock, freeblocksize, 1, NULL, NULL);
    validate_block(freeblock,freeblocksize,1);
   
    //Add back the free block in a link list
    int bin = find_memory_bin(GETSIZE(freeblock->size));    
    
    addnode(bin, freeblock);
    return;
}


static size_t highest(size_t in) {
    size_t num_bits = 0;

    while (in != 0) {
        ++num_bits;
        in >>= 1;
    }

    return num_bits;
}


boundary get_previous_block( boundary block){
    
    boundary retblock = NULL;
    block -= 1;
    if(((char*)block - heap_head) > 0){
        block = (boundary)(((char*)block - GETSIZE(block->size) - BOUNDARYSIZE));
        if(((char*)block - heap_head) >= 0){
            if(validate_block(block,0,-1))
                retblock = block;
        }
    }
    return  retblock;
}

boundary get_next_block( boundary block){

    boundary retblock = NULL;
    size_t size = GETSIZE(block->size);
    block = (boundary)( (char*)block + 2*BOUNDARYSIZE + size);
    if(((char*)block - (heap_head + heap_size)) < 0){
        if(validate_block(block,0,-1))
            retblock = block;
    }
    return retblock;
}

/* Coalse right block with the left block and 
    mark the resulting block as free   */
boundary coalse_blocks(boundary left, boundary right){
  
    size_t total_size = GETSIZE(left->size) + 2*BOUNDARYSIZE + GETSIZE(right->size);
    total_size = total_size | 1; //set free bit on
    left->size = total_size;
    boundary* nextfree = NEXTPTR(left);
    boundary* prevfree = PREVPTR(left);
    *nextfree = NULL; //Since this is a free node now, clear our garbage nodes, otherwise this corrupts memory
    *prevfree = NULL; //Same as above
    boundary finalfooter = GETFOOTERFROMHEADER(left);
    finalfooter->size = total_size;
    validate_block(left, GETSIZE(total_size), 1);
    return left;
}

/*  If ptr is NULL, nothing is done
    If ptr is called on memory that is already free, NOP
    If ptr is something not returned by malloc, NOP
*/
void free(void* ptr) {

    //nfree++;
    if( ptr == NULL)
        return;

    boundary block = (boundary)((char*)ptr - BOUNDARYSIZE);
  
    if(validate_block(block,0,-1)==0){
        //throw errow here,maybe
        return;
    }
   
    if( GETFREEBIT(block) == 1){ //Already free block
        return;
    }
    
    //Now mark this block as free  
    boundary footer = GETFOOTERFROMHEADER(block);
    block->size = block->size | 1;
    footer->size = footer->size | 1;
    boundary* n = NEXTPTR(block);
    boundary* p = PREVPTR(block);
    *n = NULL; //Since this is a free node now, clear our garbage nodes, otherwise this corrupts memory
    *p = NULL; //Same as above
    validate_block( block, 0, 1);

    boundary leftblock = get_previous_block(block);
    boundary rightblock = get_next_block(block);
    validate_block(leftblock,0,-1);
    validate_block(rightblock,0,-1);
    if(leftblock!=NULL && GETFREEBIT(leftblock) == 1){
        int bucket_number = find_memory_bin(GETSIZE(leftblock->size));
        delete_from_list(bucket_number, leftblock); 
        block = coalse_blocks(leftblock, block);
        validate_block(block,0,-1);
    }

    if(rightblock!=NULL && GETFREEBIT(rightblock) == 1){
        int bucket_number = find_memory_bin(GETSIZE(rightblock->size));
        delete_from_list(bucket_number, rightblock);
        block = coalse_blocks(block, rightblock);
        validate_block(block,0,-1);
    }
    
    int bucket_number = find_memory_bin(GETSIZE(block->size));
    addnode(bucket_number, block);
    //heap_checker((boundary)heap_head);
    //ll_checker();
    return;
}

void *malloc(size_t size) {
    
    //nmalloc++;
    if(size<=0)
        return NULL;

    void* ret_memory = NULL; //this would get the final assigned memory
    //sprintf(temp, "Malloc request for %lu bytes\n", size); pps(temp);
    size = align(size);
    int bucket_number = find_memory_bin(size);
    size_t total = size + BOUNDARYSIZE + BOUNDARYSIZE;
    boundary allocated_block = NULL;

    if(total < 0){ //this means overflow happened
        return NULL;
    }
    int iter;
    for(iter=0;iter<2;iter++){
        allocated_block = find_free_fit(bucket_number, size);
        if(allocated_block!=NULL){
            if(check_if_splittable(allocated_block, size)){
                split_block(allocated_block, size);
            }

            //Now mark both and header and footer used
            allocated_block->size = SETUSED(allocated_block->size);
            GETFOOTERFROMHEADER(allocated_block)->size = allocated_block->size;
            validate_block(allocated_block, 0, 0);
            ret_memory = allocated_block + 1;
            break;
        }else{
            int result = extend_heap(total);
            if(!result){
                //pps("Extend heap didnot work");
                return NULL;
            }
        } 
    }

    if(allocated_block==NULL){
        //pps("Allocated block is still null");
        return NULL;
    }
    
    //heap_checker((boundary)heap_head);
    //ll_checker();
    return ret_memory;
}

void* realloc(void *ptr, size_t size) {
    
    if(ptr == NULL){
        void *ret = malloc(size);
        return ret;    
    }
    size_t old_size = 0; // XXX Set this to the size of the buffer pointed to by ptr 
    boundary h = ((boundary)ptr) - 1;
    
    if(!validate_block(h, 0, -1)){
        return NULL;
    }

    old_size = GETSIZE(h->size);

    if(size == 0){
        free(ptr);
        return NULL;
    }

    void* ret = malloc(size);

    if (ret) {
        if (ptr) {
            memmove(ret, ptr, old_size < size ? old_size : size);
            free(ptr);
            return ret;
        }
    } else {
        errno = ENOMEM;
        return NULL;
    }
    return NULL;
}

void* calloc(size_t number, size_t size) {
    size_t number_size = 0;

    /* This prevents an integer overflow.  A size_t is a typedef to an integer
     * large enough to index all of memory.  If we cannot fit in a size_t, then
     * we need to fail.
     */
    if (highest(number) + highest(size) > sizeof(size_t) * CHAR_BIT) {
        errno = ENOMEM;
        return NULL;
    }

    number_size = number * size;
    void* ret = malloc(number_size);

    if (ret) {
        memset(ret, 0, number_size);
    }

    return ret;
}