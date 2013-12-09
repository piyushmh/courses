import sys, struct, os, random, time
import LFS
import Disk
import Segment
import InodeMap
import Cleaner
import pdb

from threading import Thread, Lock, Condition, Semaphore
from Disk import DiskClass
from Segment import SegmentManagerClass
from LFS import LFSClass
from InodeMap import InodeMapClass
from Inode import Inode
from FSE import FileSystemException

# given a pathname, converts into a canonical, absolute path
# by prepending the current directory when necessary
def canonicalize(path, curdir):
    if path == '':
        return curdir
    elif path[0] != '/':
        return "%s%s%s" % (curdir, '/' if curdir[-1:] != '/' else '', path)
    else:
        return path

CLEANERFLAG = True

class Shell:
    def __init__(self):
        self.currentDirectory = "/"

    def help(self, args):
        print "try making a new disk with mkfs, then do create, ls, cat, mkdir, cd, rmdir, etc"

    # creates a brand new filesystem, or else
    # mounts the last filesystem that was created with mkfs previously
    def mkfs(self, args):
        str = ""
        if len(args) > 2:
            str+="Usage: mkfs [-reuse]"
            return str
        brandnew=True
        if len(args) > 1:
            if args[1] == "-reuse":
                brandnew = False
            else:
                str+="Usage: mkfs [-reuse]"
                return str
        segmentmonitor = Cleaner.SegmentMonitor()
        Disk.disk = DiskClass(brandnew=brandnew)
        Segment.segmentmanager = SegmentManagerClass(segmentmonitor)
        InodeMap.inodemap = InodeMapClass()
        LFS.filesystem = LFSClass(initdisk=brandnew)
        if CLEANERFLAG:
            Cleaner.cleaner = Cleaner.CleanerClass(segmentmonitor)
            Cleaner.cleaner.start() #Starting the cleaner thread
        if brandnew:
            Inode.inodeidpool = 1 #Resetting this to 1 because mkfs might be run multiple times
            rootinode=Inode(isdirectory=True) #We make the root inode here
        else:
            LFS.filesystem.restore()
        return "1"

    def create(self, args):
        if len(args) != 3:
            str+= "Usage: create filename length"
            return str
        fd = LFS.filesystem.create(canonicalize(args[1], self.currentDirectory))
        # construct a string of the right size
        repeatstr = "abcdefghijklmnopqrstuvwxyz0123456789"
        str = ""
        while len(str) < int(args[2]):
            str += repeatstr
        str = str[0:int(args[2])]
        pdb.set_trace()
        fd.write(str)
        fd.close()
        return "1"

    def ls(self, args):
        curdirpath = canonicalize(args[1] if len(args) > 1 else '', self.currentDirectory)
        dd = LFS.filesystem.open(curdirpath, isdir=True)
        s = ""
        for name, inode in dd.enumerate():
            size, isdir = LFS.filesystem.stat("%s%s%s" % (curdirpath, '/' if curdirpath[-1:] != '/' else '', name))
            s+="{:<10}  inode={:<3}  type={:<4}  size={:<5}".format(name, inode, "DIR" if isdir else "FILE", size)
            s+="\n"
        return  s[:-1]

    def cat(self, args):
        s=""
        if len(args) != 2:
            s+="Usage: cat filename"
            return s
        fd = LFS.filesystem.open(canonicalize(args[1], self.currentDirectory))
        #pdb.set_trace()
        data = fd.read(50000000)
        s+= data  
        fd.close()
        return s

    def write(self, args):
        str = ""
        if len(args) < 3:
            str+="Usage: write filename data"
            return str
        fd = LFS.filesystem.open(canonicalize(args[1], self.currentDirectory))
        fd.write(args[2])
        fd.close()
        return "1"

    def mkdir(self, args):
        str = ""
        if len(args) != 2:
            str+= "Usage: mkdir dirname"
            return str
        #pdb.set_trace()
        LFS.filesystem.create(canonicalize(args[1], self.currentDirectory), isdir=True)
        return "1"

    def cd(self, args):
        # We have to check if the given path is valid!!
        str= ""
        if len(args) != 2:
            str+="Usage: cd dirname"
            return str

        dirname = canonicalize(args[1], self.currentDirectory)
        size, isdir = LFS.filesystem.stat(dirname)
        if isdir:
            self.currentDirectory = dirname
        else:
            raise FileSystemException("Not a Directory")
        return "1"

    # writes the contents of all in-memory data structures to the disk
    def sync(self, args):
        #pdb.set_trace()
        LFS.filesystem.sync()
        return "1"

    def rm(self, args):
        # XXX - do this tomorrow! after the meteor shower!
        str = ""
        if len(args)!=2:
            str+="Usage: rm filename"
            return str
        LFS.filesystem.unlink(canonicalize(args[1], self.currentDirectory))
        return "1"

    def rmdir(self, args):
        # XXX - do this tomorrow! after the meteor shower!
        str = ""
        if len(args)!=2:
            str+="Usage: rmdir dirname"
            return str
        LFS.filesystem.unlink(canonicalize(args[1], self.currentDirectory), isdir=True)
        return "1"

    def quit(self, args):
        print "\nSo Long, and Thanks for All the Fish!"
        os._exit(0)

    def exit(self, args):   
        self.quit(args)

def shellmainloop():
    while True:
        try:
            commandline = raw_input("[LFS] " + shell.currentDirectory + "> ")
            commandline = commandline.strip()
        except EOFError:
            shell.exit(None)
        pieces = commandline.split(" ")

        try:
            func = getattr(shell, pieces[0])
        except AttributeError:
            print "I don't understand what you are saying but the answer is 42."
            continue

        try:
            str = func(pieces)
            if str!= "1" and str!="":
                print str
        except FileSystemException, fse:
            print "Error: %s" % fse

shell = Shell()
if __name__ == "__main__":
    shellmainloop()