#!/usr/bin/python

import oauth

from lxml import etree
import exceptions
import errno
import urllib2
import os
import tempfile
import datetime
from time import time


class TreeEntry:
    def __init__(self, link, filetype):
        self.link = None
        self.fileType = filetype
        self.size = 0
        self.fileLink = None
        self.localFile = None
        self.Children = {}
        self.time = {}

class CollectionEntry:
    def __init__(self, title, filetype, photolink = None):
        self.title = title
        self.filetype = filetype
        self.fileLink = photolink
        self.time = {}

def dateFromAtom(datestr):
    return datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

class AlbumStruct:
    def __init__(self):
        self.Children = {}
        self.Roots = []
        self.Entries = {}
        self.Links = {}
        self.Tree = TreeEntry(None, 'album')
        self.Tree.time['access'] = datetime.datetime.now()
        self.Tree.time['modify'] = self.Tree.time['access']
        self.Tree.time['create'] = self.Tree.time['access']
        if oauth.Token:
            self.AuthHeader = {'Authorization': 'OAuth ' + oauth.Token}
        else:
            self.AuthHeader = {}
        print self.AuthHeader
#       self.BaseUrl = "http://localhost"
        self.fetchData()
        self.growTree()

    def urlopen_(self, url):
        return urllib2.urlopen(urllib2.Request(url, None, self.AuthHeader))

    def fetchData(self):
        serviceDocument = etree.XML(self.urlopen_("http://api-fotki.yandex.ru/api/me/").read())
        nsmap = { 'app' : 'http://www.w3.org/2007/app', 'atom': 'http://www.w3.org/2005/Atom', 'f' : 'yandex:fotki'} 
        albumXPath = etree.XPath('//app:collection[@id="album-list"]/@href', namespaces = nsmap)
        photoXPath = etree.XPath('//app:collection[@id="photo-list"]/@href', namespaces = nsmap)
        entriesXPath = etree.XPath('//atom:entry', namespaces = nsmap)
        selfLinkPath = etree.XPath('atom:link[@rel="self"]/@href', namespaces = nsmap)
        albumLinkPath = etree.XPath('atom:link[@rel="album"]/@href', namespaces = nsmap)
        editMediaLinkPath = etree.XPath('atom:link[@rel="edit-media"]/@href', namespaces = nsmap)
        titlePath = etree.XPath('atom:title/text()', namespaces = nsmap)
        publishedPath = etree.XPath('atom:published/text()', namespaces = nsmap)
        editedPath = etree.XPath('app:edited/text()', namespaces = nsmap)
        updatedPath = etree.XPath('atom:updated/text()', namespaces = nsmap)

        albumUrl = albumXPath.evaluate(serviceDocument)[0]
        photoUrl = photoXPath.evaluate(serviceDocument)[0]

        AlbumCollection = etree.XML(self.urlopen_(albumUrl).read())
        PhotoCollection = etree.XML(self.urlopen_(photoUrl).read())
        for album in entriesXPath.evaluate(AlbumCollection) :
            SelfLink = selfLinkPath.evaluate(album)[0]
            AlbumLink = albumLinkPath.evaluate(album)
            if AlbumLink:
                AlbumLink = AlbumLink[0]
                if self.Children.get(AlbumLink):
                    self.Children[AlbumLink].append(SelfLink)
                else:
                    self.Children[AlbumLink] = [SelfLink]
            else:
                self.Roots.append(SelfLink);
            self.Entries[SelfLink] = CollectionEntry(titlePath.evaluate(album)[0], 'album')
            self.Entries[SelfLink].time['create'] = dateFromAtom(publishedPath.evaluate(album)[0])
            self.Entries[SelfLink].time['modify'] = dateFromAtom(editedPath.evaluate(album)[0])
            self.Entries[SelfLink].time['access'] = dateFromAtom(updatedPath.evaluate(album)[0])
        
        for photo in entriesXPath.evaluate(PhotoCollection):
            SelfLink = selfLinkPath.evaluate(photo)[0]
            AlbumLink = albumLinkPath.evaluate(photo)[0]
            FileLink = editMediaLinkPath.evaluate(photo)[0]

            if self.Children.get(AlbumLink):
                self.Children[AlbumLink].append(SelfLink)
            else:
                self.Children[AlbumLink] = [SelfLink]
            self.Entries[SelfLink] = CollectionEntry(titlePath.evaluate(photo)[0], 'photo', FileLink)
            self.Entries[SelfLink].time['create'] = dateFromAtom(publishedPath.evaluate(photo)[0])
            self.Entries[SelfLink].time['modify'] = dateFromAtom(editedPath.evaluate(photo)[0])
            self.Entries[SelfLink].time['access'] = dateFromAtom(updatedPath.evaluate(photo)[0])
                
    def growTree(self):
        for Root in self.Roots:
            entry = self.Entries[Root]
            title = entry.title.encode('utf-8')
            self.Tree.Children[title] = TreeEntry(Root, 'album')
            self.Tree.Children[title].time = entry.time
            self.AddChildren(Root, self.Tree.Children[title].Children)
    

    def AddChildren(self, Root, Children):
        for Child in self.Children.get(Root, []):
            entry = self.Entries[Child]
            title = entry.title.encode('utf-8')
            Children[title] = TreeEntry(Child, entry.filetype)
            Children[title].time = entry.time
            if entry.filetype == 'photo':
                Children[title].fileLink = entry.fileLink

            self.AddChildren(Child, Children[title].Children)

    def Dump(self):
        print 'Links'
        for item in self.Links.items():
            print item[0]
        print 'Roots'
        for item in self.Roots:
            print "%s" % (item)
        print 'Tree'
        print self.Tree

    def _getEntry(self, path):
        entry = self.Tree
        for element in path:
            if element:
                if element not in entry.Children.keys():
                    raise exceptions.OSError(errno.ENOENT, "No such file or directory", '/'.join(map(str, path)))
                entry = entry.Children[element]
        return entry
    
    def Dir(self, path):
        return self._getEntry(path).Children.keys()

    def FileType(self, path):
        return self._getEntry(path).fileType

    def ReadFile(self, path, size, offset):
        entry = self._getEntry(path)
        if not entry.localFile:
            if entry.fileType == 'album':
                raise exceptions.OSError(errno.EISDIR, "File is directory", '/'.join(map(str, path)))
            u = self.urlopen_(entry.fileLink)
            content = u.read()
            f = tempfile.mkstemp()
            os.write(f[0], content)
            os.close(f[0])
            entry.localFile = f[1] 
        
        fd = os.open(entry.localFile, os.O_RDONLY)
        os.lseek(fd, offset, os.SEEK_SET)
        result = os.read(fd, size)
        os.close(fd)
        return result
        
    def GetFileSize(self, path):
        entry = self._getEntry(path)

        if entry.fileType == 'photo' and entry.size == 0:
            u = self.urlopen_(entry.fileLink)
            entry.size = int(u.info().getheader('Content-Length'))
        return entry.size

    def GetTime(self, path, element):
        entry = self._getEntry(path)
        try:
            result =  entry.time[element].strftime("%s")
            if result:
                return int(result)
        finally:
            int(time())
            
