README



Features implemented and tested:

mkfs
create filename size
cat filename
write filename string
ls directoryname
mkdir dirname
cd dirname
sync
exit/quit


Cleaner Thread - I have implemented a cleaner thread in Cleaner.py. For segment summary block I have used the last 8 bytes of every block on disk to store the inode number and the file offset for that block. So essentially I am storing information per block. Every block as 1016 bytes of data and 8 bytes of metadata. I took this decision because super block is not big enought to store the complete segment summary block. Blocks which are inodes have a special offset INODEIDENTIFIEROFFSET and blocks which are single direct blocks have a special offset INDIRECTBLOCKOFFSET.Both of these are declared in Constants.py. So essentially each block size on disk is 1016 bytes. Both these values are greater than a valid offset of a data block so there would be no collision. I have synchronized access to segments using a SegmentMonitor. If a segment is the current loaded segment the cleaner skips it moves on to the next segment. So any segment which is not in memory is potentially safe since we never overwrite a segment in LFS. Also the segmentManger takes a lock on the currently loaded segment in memory. Segment monitor has a map which tells which segments have been locked.


Extra Credit 

MultiThreaded - The only shared data structures here are the inode map and the current segment loaded in memory by segment manager. Since the segments present on the disk as only read from, there is no need to add locking on it. We are assuming that in LFS design we dont overwrite or append to already written blocks. We only read them and rewrite them in new blocks.This design is thread safe due to the following reasons 

1) All access to inodemap is synchronized. InodeMap class has a lock and every access to the inode mapping is through the methods of the InodeMap class. Since every method is under a lock)Monitor), this is thread safe.

2) Every thread while loading and writing to a segment in memory first acquires a lock on it. Even the cleaner running in the background acquires a lock on it. This means that if a thread has a segment as current segment no other segment would have it as its current segment. But they can still read that segment from the disk. When a thread flushes a segment it releases the lock on it and picks up a lock on the next available segment which has free blocks and is not being taken by any other thread.



Test cases:

1) Make file
2) Delete file
3) Make dir
4) Delete Dir
5) rmdir file - Error 
5) rm Dir - Error
6) Write to a file and verify by cat
7) cat file and verify content
8) sync, quit and verify contents
9) Create a very big file(greater than disk size) and verify exceptiom

