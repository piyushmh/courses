import sys, struct, os, random, math, pickle
import Disk
import Segment
import InodeMap

from InodeMap import InodeMapClass
from Constants import BLOCKSIZE

NUMDIRECTBLOCKS = 100 # can have as many as 252 and still fit an Inode in a 1024 byte block
inodeidpool = 1  # 1 is reserved for the root inode

def getmaxinode():
    return inodeidpool
def setmaxinode(maxii):
    global inodeidpool
    inodeidpool = maxii

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
    def _adddatablock(self, blockoffset, blockaddress):
        if blockoffset < len(self.fileblocks):
            # place this block in one of the direct data blocks
            self.fileblocks[blockoffset] = blockaddress
        else:
            # XXX - do this after the meteor shower!
            pass

    def _datablockexists(self, blockoffset):
        if blockoffset < len(self.fileblocks):
            return self.fileblocks[blockoffset] != 0
        else:
            # XXX - do this after the meteor shower!
            pass

    # given the number of a data block inside a file, i.e. 0 for
    # the first block, 1 for the second and so forth, returns
    # the contents of that block as a string
    def _getdatablockcontents(self, blockoffset):
        if blockoffset < len(self.fileblocks):
            blockid = self.fileblocks[blockoffset]
        else:
            # XXX - do this after the meteor shower!
            pass
        return Segment.segmentmanager.blockread(blockid)

    # perform a read of the file/directory pointed to by
    # this inode, for the specified length, starting at
    # the given offset
    def read(self, offset, length):
        currentblock = int(math.floor(float(offset) / BLOCKSIZE))
        inblockoffset = offset % BLOCKSIZE
        amounttoread = min(length, self.filesize - offset)
        moretoread = amounttoread
        data = ""
        while moretoread > 0:
            contents = self._getdatablockcontents(currentblock)
            newdata = contents[inblockoffset:]
            inblockoffset = 0
            moretoread -= len(newdata)
            data += newdata
            currentblock += 1

        return data[0:min(len(data), amounttoread)]

    # perform a write of the given data, starting at the file offset
    # provided below.
    def write(self, offset, data, skip_inodemap_update=False):
        size = len(data)
        currentblock = int(math.floor(float(offset) / BLOCKSIZE))
        inblockoffset = offset % BLOCKSIZE
        moretowrite = size
        while moretowrite > 0:
            # check to see if the file has any data blocks at all
            if self._datablockexists(currentblock):
                # get the old data from the block
                olddata = self._getdatablockcontents(currentblock)
                # slice and dice so we combine the new data with the old
                newdata = olddata[0:inblockoffset] + data[0:(BLOCKSIZE - inblockoffset)] + olddata[inblockoffset + len(data):]
            else:
                newdata = data[0:BLOCKSIZE]
            # allocate a new data block
            datablock = Segment.segmentmanager.write_to_newblock(newdata)
            self._adddatablock(currentblock, datablock)
            moretowrite -= (BLOCKSIZE - inblockoffset)
            data = data[(BLOCKSIZE - inblockoffset):]
            inblockoffset = 0
            currentblock += 1

        self.filesize = max(self.filesize, offset + size)
        if not skip_inodemap_update:
            InodeMap.inodemap.update_inode(self.id, self.serialize())
