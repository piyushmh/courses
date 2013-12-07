import sys, struct, os, random, math, pickle
import Disk
import Segment
import InodeMap
from FSE import FileSystemException

import pdb

from InodeMap import InodeMapClass
from Constants import BLOCKSIZE , INDIRECTBLOCKOFFSET, MAXDATABLOCKSINODE, NUMDIRECTBLOCKS


inodeidpool = 1  # 1 is reserved for the root inode

def getmaxinode():
    return inodeidpool
def setmaxinode(maxii):
    global inodeidpool
    inodeidpool = maxii

DEBUG = False

class Inode:
    def __init__(self, str=None, isdirectory=False):
        global inodeidpool
        if str is not None:
            self.id = struct.unpack("I", str[0:4])[0]
            str = str[4:]
            self.filesize = struct.unpack("I", str[0:4])[0]
            str = str[4:]
            self.fileblocks = [0] * NUMDIRECTBLOCKS
            for i in range(0, NUMDIRECTBLOCKS):
                self.fileblocks[i] = struct.unpack("I", str[0:4])[0]
                str = str[4:]
            self.indirectblock = struct.unpack("I", str[0:4])[0]
            str = str[4:]
            self.isDirectory = struct.unpack("?", str[0])[0]
        else:
            self.id = inodeidpool
            inodeidpool += 1
            self.filesize = 0
            self.fileblocks = [0] * NUMDIRECTBLOCKS
            self.indirectblock = 0
            self.isDirectory = isdirectory
            # write the new inode to disk
            if DEBUG:
                print "Initializing inode with id ",self.id, " HERE1" #SEE 
            InodeMap.inodemap.update_inode(self.id, self.serialize())
            
    # returns a serialized version of the Inode that fits in a fixed
    # size data block
    def serialize(self):
        str = ""
        str += struct.pack("I", self.id)
        str += struct.pack("I", self.filesize)
        for i in range(0, NUMDIRECTBLOCKS):
            str += struct.pack("I", self.fileblocks[i])
        str += struct.pack("I", self.indirectblock)
        str += struct.pack("?", self.isDirectory)
        return str

    # given the number of a data block inside a file, i.e. 0 for
    # the first block, 1 for the second and so forth, and a
    # physical address for that block, updates the inode to
    # point to that particular block
    # Adding code for indirect blocks as well
    # caller should make sure that the blockoffset would fit in a inode
    def _adddatablock(self, blockoffset, blockaddress):
        if blockoffset < len(self.fileblocks):
            # place this block in one of the direct data blocks
            self.fileblocks[blockoffset] = blockaddress
        else:
            # XXX - do this after the meteor shower! - alrighty almighty
            newdata = ""
            blockoffset = blockoffset-len(self.fileblocks)
            if not self.indirectblock:  #this means the indirect block hasnt been allocated
                if len(self.fileblocks)!= (blockoffset+len(self.fileblocks)):
                    print "Alert 1, this should not have happened"
                for i in range(0, BLOCKSIZE/4):
                    if i == blockoffset:
                        newdata += struct.pack("I",blockaddress)
                    else:
                        newdata += struct.pack("I",0)
            else:
                data = Segment.segmentmanager.blockread(self.indirectblock)
                newdata = data[0:blockoffset*4]
                newdata += struct.pack("I",blockaddress)
                newdata += data[(blockoffset+1)*4:]

            self.indirectblock = Segment.segmentmanager.write_to_newblock(newdata,self.id, INDIRECTBLOCKOFFSET)

    def _datablockexists(self, blockoffset):
        if blockoffset < len(self.fileblocks):
            return self.fileblocks[blockoffset] != 0
        else:
            # XXX - do this after the meteor shower!
            if self.indirectblock == 0:
                return 0
            else:
                blockoffset -= len(self.fileblocks)
                data = Segment.segmentmanager.blockread(self.indirectblock)
                blockid = struct.unpack("I", data[4*blockoffset:4*(blockoffset+1)])[0]
                if not blockid:
                    return 0
                else:
                    return 1
            

    # given the number of a data block inside a file, i.e. 0 for
    # the first block, 1 for the second and so forth, returns
    # the contents of that block as a string
    # Adding support for indirect blocks
    def _getdatablockcontents(self, blockoffset):
        if blockoffset < len(self.fileblocks): #this is a direct block
            blockid = self.fileblocks[blockoffset]
        else:
            indirectblockid = self.indirectblock
            indirectblockcontent = Segment.segmentmanager.blockread(indirectblockid)
            blockid = self._read_from_indirect_block(indirectblockcontent, blockoffset - len(self.fileblocks))
        #Here we are returning only the data contained in the block, not the metadata
        return Segment.segmentmanager.blockread(blockid)

    # Read from indirect block, blockcontent is the content of the 
    # indirect block and the offset is the offset in it. This is assuming
    # an indirect block contains pointers to BLOCKSIZE/4 data blocks
    def _read_from_indirect_block(self,blockcontent, blockoffset):
        print "Inside Inode:_read from indirect block for offset ",blockoffset
        if blockoffset < (BLOCKSIZE/4):
            blockid = struct.unpack("I", blockcontent[blockoffset*4:(blockoffset+1)*4])[0]
            return blockid
        else:
            print "Inside Inode:_read_from_indirect_block:Block size is passed is invalid, trace back ,", blockoffset

    # perform a read of the file/directory pointed to by
    # this inode, for the specified length, starting at
    # the given offset.
    def read(self, offset, length):
        currentblock = int(math.floor(float(offset) / BLOCKSIZE))
        inblockoffset = offset % BLOCKSIZE
        amounttoread = min(length, self.filesize - offset)
        moretoread = amounttoread
        data = ""
        while moretoread > 0:
            if DEBUG:
                print "Inside Inode.read, reading block number :", currentblock
            contents = self._getdatablockcontents(currentblock)
            newdata = contents[inblockoffset:]
            inblockoffset = 0
            moretoread -= len(newdata)
            data += newdata
            currentblock += 1

        return data[0:min(len(data), amounttoread)]

    # perform a write of the given data, starting at the file offset
    # provided below. 
    # Throws error when data does not fit in the max number of blocks
    # in a file.
    # Sheer brilliance:)
    def write(self, offset, data, skip_inodemap_update=False):
        size = len(data)
        currentblock = int(math.floor(float(offset) / BLOCKSIZE))
        inblockoffset = offset % BLOCKSIZE
        moretowrite = size
        while moretowrite > 0:
            if currentblock >= MAXDATABLOCKSINODE:
                raise FileSystemException("Data exceeded max file size")
           
            # check to see if the file has any data blocks at all
            if self._datablockexists(currentblock):
                # get the old data from the block
                olddata = self._getdatablockcontents(currentblock)
                # slice and dice so we combine the new data with the old
                newdata = olddata[0:inblockoffset] + data[0:(BLOCKSIZE - inblockoffset)] + olddata[inblockoffset + len(data):]
            else:
                newdata = data[0:BLOCKSIZE]
            # allocate a new data block
            datablock = Segment.segmentmanager.write_to_newblock(newdata, self.id, currentblock)
            self._adddatablock(currentblock, datablock)
            moretowrite -= (BLOCKSIZE - inblockoffset)
            data = data[(BLOCKSIZE - inblockoffset):]
            inblockoffset = 0
            currentblock += 1

        self.filesize = max(self.filesize, offset + size)
        if not skip_inodemap_update:
            InodeMap.inodemap.update_inode(self.id, self.serialize())
