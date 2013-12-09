FILENAMELEN = 28
BLOCKSUMMARY = 8
ACTUALBLOCKSIZE = 1024
BLOCKSIZE = ACTUALBLOCKSIZE - BLOCKSUMMARY
DISKSIZE  = 1024 * ACTUALBLOCKSIZE  # a 1MB disk
SEGMENTSIZE = 256  # blocks
NUMBLOCKS = SEGMENTSIZE - 1 # number of blocks in a segment 
NUMSEGMENTS = DISKSIZE / (BLOCKSIZE * SEGMENTSIZE)

# These two numbers are used to identify if the data block is an indirect block or an innode
INDIRECTBLOCKOFFSET = 1729  #This is greater than any valid offset in an inode  (Ramanujan's number)
INODEIDENTIFIEROFFSET = 1634  #NarcissisticNumber :)
NUMDIRECTBLOCKS = 100 # can have as many as 250 and still fit an Inode in a 1024 byte block
MAXDATABLOCKSINODE = (NUMDIRECTBLOCKS + BLOCKSIZE/4)