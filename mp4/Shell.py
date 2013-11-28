import sys, struct, os, random, time
import LFS
import Disk
import Segment
import InodeMap

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

class Shell:
    def __init__(self):
        self.currentDirectory = "/"

    def help(self, args):
        print "try making a new disk with mkfs, then do create, ls, cat, mkdir, cd, rmdir, etc"

    # creates a brand new filesystem, or else
    # mounts the last filesystem that was created with mkfs previously
    def mkfs(self, args):
        if len(args) > 2:
            print "Usage: mkfs [-reuse]"
            return
        brandnew=True
        if len(args) > 1:
            if args[1] == "-reuse":
                brandnew = False
            else:
                print "Usage: mkfs [-reuse]"
                return
        Disk.disk = DiskClass(brandnew=brandnew)
        Segment.segmentmanager = SegmentManagerClass()
        InodeMap.inodemap = InodeMapClass()
        LFS.filesystem = LFSClass(initdisk=brandnew)
        if brandnew:
            rootinode=Inode(isdirectory=True)
        else:
            LFS.filesystem.restore()

    def create(self, args):
        if len(args) != 3:
            print "Usage: create filename length"
            return
        fd = LFS.filesystem.create(canonicalize(args[1], self.currentDirectory))
        # construct a string of the right size
        repeatstr = "abcdefghijklmnopqrstuvwxyz0123456789"
        str = ""
        while len(str) < int(args[2]):
            str += repeatstr
        str = str[0:int(args[2])]
        fd.write(str)
        fd.close()

    def ls(self, args):
        curdirpath = canonicalize(args[1] if len(args) > 1 else '', self.currentDirectory)
        dd = LFS.filesystem.open(curdirpath, isdir=True)
        for name, inode in dd.enumerate():
            size, isdir = LFS.filesystem.stat("%s%s%s" % (curdirpath, '/' if curdirpath[-1:] != '/' else '', name))
            print "%s\tinode=%d\ttype=%s\tsize=%d" % (name, inode, "DIR" if isdir else "FILE", size)

    def cat(self, args):
        fd = LFS.filesystem.open(canonicalize(args[1], self.currentDirectory))
        data = fd.read(50000000)
        print data
        fd.close()

    def write(self, args):
        if len(args) < 3:
            print "Usage: write filename data"
            return

        fd = LFS.filesystem.open(canonicalize(args[1], self.currentDirectory))
        fd.write(args[2])
        fd.close()

    def mkdir(self, args):
        LFS.filesystem.create(canonicalize(args[1], self.currentDirectory), isdir=True)

    def cd(self, args):
        # We have to check if the given path is valid!!
        if len(args) != 2:
            print "Usage: cd dirname"
            return

        dirname = canonicalize(args[1], self.currentDirectory)
        size, isdir = LFS.filesystem.stat(dirname)
        if isdir:
            self.currentDirectory = dirname
        else:
            raise FileSystemException("Not a Directory")

    # writes the contents of all in-memory data structures to the disk
    def sync(self, args):
        LFS.filesystem.sync()

    def rm(self, args):
        # XXX - do this tomorrow! after the meteor shower!
        pass

    def rmdir(self, args):
        # XXX - do this tomorrow! after the meteor shower!
        pass

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
            func(pieces)
        except FileSystemException, fse:
            print "Error: %s" % fse
shell = Shell()
if __name__ == "__main__":
    shellmainloop()
