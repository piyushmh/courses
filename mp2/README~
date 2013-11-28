MP 2


ENVIRONMENT 

The code was developed on 64 bit Ubuntu on gcc 4.7.3.



DESIGN AND IMPLEMENTATION


Summary 

Heap memory is tracked in blocks. Each block has a HEADER and FOOTER which contains a variable indicating the size 
of the block (8 bytes each). Free blocks use the data section to store pointers to previous and next free blocks, since 
the data section is unused in free block anyway. The memory returned is always 16 aligned since I need to the block
when it is freed to be able to store two additionnal 8 bytes pointers as well (See the Free Block structure below). 
This might add some internal fragmentation but this would enable the HEADER size to be 8 bytes only. 
Since the last 4 bits of the variable storing size is always 0, the LSB of the size variable in header and footer is 
used to track whether a block is free or not. Free block list are binned according to their size. This would considerably
speed up the lookup time for free block during malloc.

Amount of memory used per block- 16 bytes.



Description

Used block : Each used block has a header and a footer which contains an variable of the type size_t to store the size
of the block. The LSB of this size variable is used to store that this block is used.

***************************
* H *                 * F *
* E *      DATA       * O *
* A *                 * O *
* D *                 * T *
* E *                 * E *
* R *                 * R *
***************************

Free block :  Each free block in addition to having a header and a footer described above also has pointers to next and free
blocks. The data part of the block since it is free anyways is used to store these variables.There are 7 bins in the system each having blocks in a definite size range.

***************************
* H * N * P *         * F *
* E * X * V *  EMPTY  * O *
* A * T * S *         * O *
* D * P * P *         * T *
* E * T * T *	      * E *
* R * R * R *         * R *
***************************


Bins : Free block are linked together according to their size range. The head of all such link lists are stored in 
a static array. This enables malloc to search in link lists of appropriate sizes.


Bin 0  (Size 1-16)   	------> Free block link list
Bin 1  (Size 17-32)		------> Free block link list
Bin 2  (Size 33-64)		------> Free block link list
Bin 3  (Size 65-128)	------> Free block link list
Bin 4  (Size 129-256)	------> Free block link list
Bin 4  (Size 129-256)	------> Free block link list
Bin 5  (Size 257-512)	------> Free block link list
Bin 6  (Size 513-1024)	------> Free block link list



MALLOC 

Whenever malloc is called a search is done on a free block list list to find a block which would serve the request.
Free block link list are maintained in different bins according to sizes.
A link list is selected according to the size requested by the user and a linear search is performed. The first block
satifying the request (FIRST FIT) is selected and is used to serve the request. Since the blocks are binned according to 
different sizes, this linear search is generally very fast. If the request cannot be fulfilled by that link list, a search 
in a higher sized bin happens. If no such bin is found in any of the link list then system call is done to fetch that memory.
If the request is less than 1024, then 1024 bytes is requested since we want to minimize the system calls done to the system. 
Requested block is returned to the user and the remaining chunk is added to the approproate free block bin.
Worst case time complexity  - Linear in size of free blocks of that range of the request bytes.

Optimization 

I tried to convert the linear list list of free blocks to a balanced binary searched tree(red black tree).
This would then reduce the worst case run time of malloc to log(n) where n are the number of free nodes in that list.
This would probably not affect the average case run time of malloc much since we are using binning, but this can for some 
special cases avoid long linear look ups. I couldnt get that code to work properly and it was still segfaulting. So I have 
submitted the code for the linear link list only.



FREE 
 
Whenever a block is being freed, a check is done to find out if the block just to the left of it and the block just to the 
right of it is free or not. This operation is O(1) since every block has a fixed size and header and footer both containing
size of the block. If any one of them is free, they are coalsed with the block returned and then they are added back to the
appropriate link list. The coalsed block is added to the head of the corresponding link list.

Worst case time complexity - O(1)




