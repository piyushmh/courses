#!/usr/bin/python
import sys, struct, os, random, time
import Disk
from FSE import FileSystemException

from Constants import BLOCKSIZE, DISKSIZE, SEGMENTSIZE, NUMSEGMENTS

NUMBLOCKS = SEGMENTSIZE - 1 # number of blocks in a segment (one less than SEGMENTSIZE because of the superblock)

DEBUG = False

# the segmentmanager manages the current segment, flushing it
# to disk as necessary and picking up another segment to work on
class SegmentManagerClass:
    def __init__(self):
        self.segcounter = 0
        self.currentseg = SegmentClass(self.segcounter)

    # write the given data to a free block in the current segment.
    # if no free block exists, find another segment with a free block in it
    def write_to_newblock(self, data):
        # XXX - do this tomorrow! after the meteor shower!
        pass

    # read the requested block if it is in memory, if not, read it from disk
    def blockread(self, blockno):
        if self.is_in_memory(blockno):
            return self.read_in_place(blockno)
        else:
            return Disk.disk.blockread(blockno)

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
        if len(data) != len(self.currentseg.blocks[blockoffset]):
            print "Assertion error 1: data being written to segment is not the right size (%d != %d)" % (len(data), len(self.currentseg.blocks[blockoffset]))
        else:
            self.currentseg.blocks[blockoffset] = data
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
            if superblock.inodemapgeneration > 0 and superblock.inodemapgeneration > maxgen:
                maxgen = superblock.inodemapgeneration
                imlocation = superblock.inodemaplocation
        return imlocation

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
    def write_to_newblock(self, data):
        for i in range(0, NUMBLOCKS):
            if not self.superblock.blockinuse[i]:
                if len(data) > BLOCKSIZE:
                    print "Assertion error 2: data being written to segment is not the right size (%d != %d)" % (len(data), len(self.blocks[i]))
                    print data
                    os._exit(1)
                # update the block data
                self.blocks[i] = data + self.blocks[i][len(data):]
                self.superblock.blockinuse[i] = True
                # return the physical location of the block
                return i + 1
        return -1

    def flush(self):
        #write the superblock to disk
        Disk.disk.blockwrite(self.segmentbase, self.superblock.serialize())
        #write all blocks in the segment to disk
        for i in range(0, NUMBLOCKS):
            Disk.disk.blockwrite(self.segmentbase + 1 + i, self.blocks[i])

segmentmanager = None
