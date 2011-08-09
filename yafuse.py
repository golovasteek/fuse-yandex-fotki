#!/usr/bin/python

import fuse
from fuse import Fuse

from time import time

import stat    # for file properties
import os      # for filesystem modes (O_RDONLY, etc)
import errno   # for error number codes (ENOENT, etc)
               # - note: these must be returned as negatives

import yaapi

fuse.fuse_python_api = (0, 2)

def log(message):
        l = open("./log",'a')
        l.write(message+'\n')
        l.close()

def dirFromList(list):
    """
    Return a properly formatted list of items suitable to a directory listing.
    [['a', 'b', 'c']] => [[('a', 0), ('b', 0), ('c', 0)]]
    """
    return [[(x, 0) for x in list]]

def getDepth(path):
    """
    Return the depth of a given path, zero-based from root ('/')
    """
    if path == '/':
        return 0
    else:
        return path.count('/')

def getParts(path):
    """
    Return the slash-separated parts of a given path as a list
    """
    if path == '/':
        return [['/']]
    else:
        return path.split('/')

class NullFS(Fuse):
    """
    """

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)

	self.struct = yaapi.AlbumStruct()

        print 'Init complete.'

    def getattr(self, path):
        """
        - st_mode (protection bits)
        - st_ino (inode number)
        - st_dev (device)
        - st_nlink (number of hard links)
        - st_uid (user ID of owner)
        - st_gid (group ID of owner)
        - st_size (size of file, in bytes)
        - st_atime (time of most recent access)
        - st_mtime (time of most recent content modification)
        - st_ctime (platform dependent; time of most recent metadata change on Unix,
                    or the time of creation on Windows).
        """

 #       log('*** getattr %s' % path)

#        depth = getDepth(path) # depth of path, zero-based from root
#        pathparts = getParts(path) # the actual parts of the path
	curtime = int(time())
	filetype = self.struct.FileType(path.split('/'))

	if filetype  == 'album':
		mode = stat.S_IFDIR | 0755
		fileSize = 4096
	else:
		fileSize = self.struct.GetFileSize(path.split('/'))
		mode = stat.S_IFREG | 0755

	print filetype
	
	st = fuse.Stat(st_mode = mode, st_nlink = 2, st_uid = 1000,
		st_gid = 1000, st_size = fileSize, st_atime = curtime,
		st_mtime = curtime, st_ctime = curtime)
	return st
#	return os.lstat(".")

    def readdir(self, path, offset):
        """
        return: [[('file1', 0), ('file2', 0), ... ]]
        """

        print '*** readdir %s' % path
	result = ['.', '..']
	result.extend(self.struct.Dir(path.split('/')))

	for e in result:
		yield fuse.Direntry(e)

    def mythread ( self ):
        print '*** mythread'
        return -errno.ENOSYS

    def chmod ( self, path, mode ):
        print '*** chmod', path, oct(mode)
        return -errno.ENOSYS

    def chown ( self, path, uid, gid ):
        print '*** chown', path, uid, gid
        return -errno.ENOSYS

    def fsync ( self, path, isFsyncFile ):
        print '*** fsync', path, isFsyncFile
        return -errno.ENOSYS

    def link ( self, targetPath, linkPath ):
        print '*** link', targetPath, linkPath
        return -errno.ENOSYS

    def mkdir ( self, path, mode ):
        print '*** mkdir', path, oct(mode)
        return -errno.ENOSYS

    def mknod ( self, path, mode, dev ):
        print '*** mknod', path, oct(mode), dev
        return -errno.ENOSYS

    def open ( self, path, flags ):
        print '*** open', path, flags
        #return -errno.ENOSYS
	return fuse.FuseFileInfo()

    def read ( self, path, length, offset ):
        print '*** read', path, length, offset
        #return -errno.ENOSYS
	data = self.struct.ReadFile(path.split('/'))
	return data[offset:length+offset]

    def readlink ( self, path ):
        print '*** readlink', path
        return -errno.ENOSYS

    def release ( self, path, flags ):
        print '*** release', path, flags
        return -errno.ENOSYS

    def rename ( self, oldPath, newPath ):
        print '*** rename', oldPath, newPath
        return -errno.ENOSYS

    def rmdir ( self, path ):
        print '*** rmdir', path
        return -errno.ENOSYS

#    def statfs ( self ):
#        print '*** statfs'
#        return -errno.ENOSYS

    def symlink ( self, targetPath, linkPath ):
        print '*** symlink', targetPath, linkPath
        return -errno.ENOSYS

    def truncate ( self, path, size ):
        print '*** truncate', path, size
        return -errno.ENOSYS

    def unlink ( self, path ):
        print '*** unlink', path
        return -errno.ENOSYS

    def utime ( self, path, times ):
        print '*** utime', path, times
        return -errno.ENOSYS

    def write ( self, path, buf, offset ):
        print '*** write', path, buf, offset
        return -errno.ENOSYS


if __name__ == '__main__':
    fs = NullFS()
    fs.parse(errex=1)

    fs.main()

