from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
from Constants import INODEIDENTIFIEROFFSET

import struct
import Segment

DEBUG = False
# the task of the InodeMap is to map inodes to their
# position on the disk
class InodeMapClass:
    def __init__(self):
        self.mapping = {}
        self.generationcount = 1
        self.inodemaplock = Lock() #For synchronized access to lock

    # given an abstract inode identifier, returns the
    # on-disk block address for the inode
    def lookup(self, inodeno):
        with self.inodemaplock:
            if not self.mapping.has_key(inodeno):
                if DEBUG:
                    print "Lookup for inode failed because that inode was never created", inodeno
                return None
            else:
                return self.mapping[inodeno]

    # following the write of an inode, update the
    # inode map with the new position of the inode
    # on the disk
    def update_inode(self, inodeid, inodedata):
        if DEBUG:
            print "Inside InodeMapClass:update_inode for inodeid :", inodeid
        inodeblockloc = Segment.segmentmanager.write_to_newblock(inodedata, inodeid,INODEIDENTIFIEROFFSET)
        if DEBUG:
            print "Inside InodeMapClass:update_inode for blockid :", inodeblockloc
        with self.inodemaplock:
            self.mapping[inodeid] = inodeblockloc

    # write the inodemap to the end of the current segment
    #
    # the inode map is written to an invisible file, whose
    # inode in turn is stored in the superblock of the
    # segment
    def save_inode_map(self, iip):
        with self.inodemaplock:
            self.generationcount += 1
            str = struct.pack("I", iip) # Save maximum inodenumber
            for (key, val) in self.mapping.items():
                str += struct.pack("II", key, val)
            return str, self.generationcount

    # go through all segments, find the
    # most recent segment, and read the latest valid inodemap
    # from the segment
    def restore_inode_map(self, imdata):
        #print repr(imdata)
        with self.inodemaplock:
            self.mapping = {}
            iip = struct.unpack("I", imdata[0:4])[0]
            imdata = imdata[4:]
            for keyvaloffset in range(0, len(imdata), 8):
                key, val = struct.unpack("II", imdata[keyvaloffset:keyvaloffset + 8])
                self.mapping[key] = val
            return iip

    def remove_mapping(self, inodeid):
        with self.inodemaplock:
            if inodeid in self.mapping:
                del self.mapping[inodeid]
                return 1
            else:
                return -1


inodemap = None
