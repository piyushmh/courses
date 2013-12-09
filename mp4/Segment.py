#!/usr/bin/python
import sys, struct, os, random, time
import Disk
from FSE import FileSystemException
from Cleaner import SegmentMonitor
from Constants import BLOCKSIZE, DISKSIZE, SEGMENTSIZE, NUMSEGMENTS, ACTUALBLOCKSIZE, NUMBLOCKS

#(one less than SEGMENTSIZE because of the superblock)

DEBUG = False

# the segmentmanager manages the current segment, flushing it
# to disk as necessary and picking up another segment to work on
class SegmentManagerClass:
    def __init__(self, segmentmonitor):
        self.segcounter = 0
        self.segmentmonitor = segmentmonitor
        if self.segmentmonitor.acquire_segment_lock(self.segcounter)==1:
            self.currentseg = SegmentClass(self.segcounter)

    # write the given data to a free block in the current segment.
    # if no free block exists, find another segment with a free block in it
    # This accepts only a single block of data, returns the block allocated
    # Returns -1 if data >BLOCKSIZE or if disk ran out of memory
    # Inodeid and blockoffset are part of meta data stored with each block
    def write_to_newblock(self, data, inodeid, blockoffset):
        # XXX - do this tomorrow! after the meteor shower! - Okay bro!!
        if DEBUG:
            print "Inside SegmentManager:write_to_newblock for datasize :", len(data) #SEE
        retval = -1
        if len(data) > BLOCKSIZE: # NOTE- Add exception later
            print "Inside SegmentManager:write_to_newblock :Data length greater than Block size for data :", data
            return -1
        retval = self.currentseg.write_to_newblock(data[:BLOCKSIZE], inodeid, blockoffset)
        if retval == -1:
            result = self._flush_and_initialize_new_segment()
            if result == -1:
                raise FileSystemException("Disk out of space, exiting")
            else:
                retval = self.currentseg.write_to_newblock(data[:BLOCKSIZE], inodeid, blockoffset)

        return (retval + self.currentseg.segmentbase)
            

    # Flushes the current segment into disk. Then keeps assigning
    # currseg to the next segment until it find a segment with a free block
    # Returns -1 if no segment if present with a free block
    def _flush_and_initialize_new_segment(self):
        self.flush()
        self.segmentmonitor.release_segment_lock(self.segcounter)
        if True:
                print "SegmentManager.Inside flush and initialize"
        for i in range(NUMSEGMENTS):
            self.segcounter = (self.segcounter+1)%NUMSEGMENTS
            if self.segmentmonitor.acquire_segment_lock(self.segcounter)==1:
                self.currentseg = SegmentClass(self.segcounter)
                if self.currentseg.check_if_segment_has_free_block() == 1:
                    return 1
                else:
                    self.segmentmonitor.release_segment_lock(self.segcounter)   
        return -1


    # read the requested block if it is in memory, if not, read it from disk
    # this method only returns data and not the metadata 
    def blockread(self, blockno):
        if self.is_in_memory(blockno):
            return self.read_in_place(blockno)[:BLOCKSIZE]
        else:
            return Disk.disk.blockread(blockno)[:BLOCKSIZE]

    # write the requested block, to the disk, or else to memory if
    # this block is part of the current segment
    def blockwrite(self, blockno, data):
        if self.is_in_memory(blockno):
            self.update_in_place(blockno, data)
        else:
            Disk.disk.blockwrite(blockno, data)

    # returns true if the given block disk address is currently in memory
    def is_in_memory(self, blockno):
        return blockno >= self.currentseg.segmentbase and blockno < (self.currentseg.segmentbase + SEGMENTSIZE)

    def update_in_place(self, blockno, data):
        if DEBUG:
            print "Writing block #%d to the segment" % blockno
        blockoffset = blockno - 1 - self.currentseg.segmentbase
        if len(data) > BLOCKSIZE:
            print "Assertion error 1: data being written to segment is not the right size (%d != %d)" % (len(data), len(self.currentseg.blocks[blockoffset]))
            raise FileSystemException("Segment.update_in_place, incorrect size passed" + str(len(data)))
        else:
            self.currentseg.blocks[blockoffset] = data + self.currentseg.blocks[blockoffset][len(data):]

    def read_in_place(self, blockno):
        if DEBUG:
            print "Reading block #%d from the segment" % blockno
        blockoffset = blockno - 1 - self.currentseg.segmentbase
        return self.currentseg.blocks[blockoffset]

    # update the current segment's superblock with the latest position & gen number of the inodemap
    def update_inodemap_position(self, imloc, imgen):
        self.currentseg.superblock.update_inodemap_position(imloc, imgen)

    # flush the current segment to the disk
    def flush(self):
        self.currentseg.flush()

    def locate_latest_inodemap(self):
        # go through all segments, read all superblocks,
        # find the inodemap with the highest generation count
        maxgen = -1
        imlocation = -1
        for segno in range(0, NUMSEGMENTS):
            superblock = SuperBlock(data=Disk.disk.blockread(segno * SEGMENTSIZE))
            #print superblock
            if superblock.inodemapgeneration > 0 and superblock.inodemapgeneration > maxgen:
                maxgen = superblock.inodemapgeneration
                imlocation = superblock.inodemaplocation
        return imlocation, maxgen

class SuperBlock:
    def __init__(self, data=None):
        if data is None:
            # the first block is the superblock and is handled specially
            self.blockinuse = [False] * NUMBLOCKS
            self.inodemapgeneration = -1
            self.inodemaplocation = -1
        else:
            # recover a superblock that was previously written to disk
            self.blockinuse = [False] * NUMBLOCKS
            for i in range(0, NUMBLOCKS):
                self.blockinuse[i] = struct.unpack('?', data[i])[0]
            self.inodemapgeneration = struct.unpack('I', data[NUMBLOCKS:NUMBLOCKS+4])[0]
            self.inodemaplocation = struct.unpack('I', data[NUMBLOCKS+4:NUMBLOCKS+8])[0]
            

    def __str__(self):
        return "InodeMapGen :" + str(self.inodemapgeneration) + "\n" + "InodeMapLoc :" + str(self.inodemaplocation)

    def serialize(self):
        str = ""
        for i in range(0, NUMBLOCKS):
            str += struct.pack('?', self.blockinuse[i])
        str += struct.pack('II', self.inodemapgeneration, self.inodemaplocation)
        return str

    # the inodemap is written to a specially created inode. the generation
    # count of that inode and its flushed location on disk is written to the
    # superblock
    def update_inodemap_position(self, imlocation, imgeneration):
        self.inodemapgeneration = imgeneration
        self.inodemaplocation = imlocation

class SegmentClass:
    def __init__(self, segmentnumber):
        self.segmentbase = segmentnumber * SEGMENTSIZE
        # read the superblock, it's the first block in the segment
        self.superblock = SuperBlock(data=Disk.disk.blockread(self.segmentbase))
        self.blocks= []
        # read the segment blocks from disk, they follow the superblock
        for i in range(self.segmentbase + 1, self.segmentbase + 1 + NUMBLOCKS):
            self.blocks.append(Disk.disk.blockread(i))

    # write data to a free block within the segment. Since the
    # segment is in memory, the write only updates the blocks in
    # memory and does not have to touch the disk
    def write_to_newblock(self, data, inodeid, blockoffset):
        for i in range(0, NUMBLOCKS):
            if not self.superblock.blockinuse[i]:
                if len(data) > BLOCKSIZE:
                    print "Assertion error 2: data being written to segment is not the right size (%d != %d)" % (len(data), len(self.blocks[i]))
                    print data
                    os._exit(1)

                # update the block data and metadata
                if (inodeid==0):
                    print "Something went wrong check"
                self.blocks[i] = data + self.blocks[i][len(data):BLOCKSIZE] + struct.pack("II", inodeid,blockoffset)
                if len(self.blocks[i])!= ACTUALBLOCKSIZE:
                    print "Alert3: Something went wrong"
                
                self.superblock.blockinuse[i] = True
                # return the physical location of the block
                return i + 1
        return -1

    #This first flushes the serialized version of superblock and then all
    # the blocks in the segment
    def flush(self):
        #write the superblock to disk
        Disk.disk.blockwrite(self.segmentbase, self.superblock.serialize())
        #write all blocks in the segment to disk
        for i in range(0, NUMBLOCKS):
            Disk.disk.blockwrite(self.segmentbase + 1 + i, self.blocks[i])

    def check_if_segment_has_free_block(self):
        for i in range(NUMBLOCKS):
            if not self.superblock.blockinuse[i]:
                return 1

        return -1

segmentmanager = None
