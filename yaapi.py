#!/usr/bin/python
import feedparser
import exceptions
import errno

class TreeEntry:
	def __init__(self, link, filetype):
		self.link = None
		self.filetype = filetype
		self.Children = {}

class AlbumStruct:
	def __init__(self):
		self.Children = {}
		self.Roots = []
		self.Entries = {}
		self.Links = {}
		self.Tree = TreeEntry(None, 'album')
		self.fetchData('golovasteek')
		self.growTree()

	def fetchData(self, UserName):
		AlbumCollection = feedparser.parse("http://api-fotki.yandex.ru/api/users/%s/albums/" % UserName)
		PhotoCollection = feedparser.parse("http://api-fotki.yandex.ru/api/users/%s/photos/" % UserName)
		for album in AlbumCollection.entries:
			AlbumLink = None
			for link in album.links:
				if link.rel == "self":
					SelfLink = link.href
				if link.rel == "album":
					AlbumLink = link.href
			if AlbumLink:
				if self.Children.get(AlbumLink):
					self.Children[AlbumLink].append(SelfLink)
				else:
					self.Children[AlbumLink] = [SelfLink]
			else:
				self.Roots.append(SelfLink);
			self.Entries[SelfLink] = album
			self.Entries[SelfLink].filetype = 'album'
		
		for photo in PhotoCollection.entries:
			AlbumLink = None
			for link in photo.links:
				if link.rel == "self":
					SelfLink = link.href
				if link.rel == "album":
					AlbumLink = link.href
			if self.Children.get(AlbumLink):
				self.Children[AlbumLink].append(SelfLink)
			else:
				self.Children[AlbumLink] = [SelfLink]
			self.Entries[SelfLink] = photo
			self.Entries[SelfLink].filetype = 'photo'
				
	def growTree(self):
		for Root in self.Roots:
			entry = self.Entries[Root]
			title = entry.title.encode('utf-8')
			self.Tree.Children[title] = TreeEntry(Root, 'album')

			self.AddChildren(Root, self.Tree.Children[title].Children)
	

	def AddChildren(self, Root, Children):
		for Child in self.Children.get(Root, []):
			entry = self.Entries[Child]
			title = entry.title.encode('utf-8')
			Children[title] = TreeEntry(Child, entry.filetype)

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
	
	def Dir(self, path):
		Children = self.Tree.Children
		for element in path:
			if element:
				if element not in Children.keys():
					raise exceptions.OSError(errno.ENOENT, "No such file or directory", '/'.join(map(str, path)))
				Children = Children[element].Children
		return Children.keys()

	def FileType(self, path):
		result = self.Tree.filetype 
		Children = self.Tree.Children
		for element in path:
			if element:
				if element not in Children.keys():
					raise exceptions.OSError(errno.ENOENT, "No such file or directory", '/'.join(map(str, path)))
				result = Children[element].filetype
				Children = Children[element].Children
		return result
