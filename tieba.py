#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This module is designed to parse images(uploaded by the users) of a specific Baidu Tieba within
all the atricles and download them automatically.

What does main() function do:
	InnerParser = InnerLinksProcessor()	#create an parser to parse inner links of the entrance page.
	
	#open the entrance page, read the HTML of the whole page.
	sock = urlopen(TARGET)
	InnerHTMLSource = sock.read()
	sock.close()

	#feed the parser of inner links, parsing start automatically.
	InnerParser.feed(InnerHTMLSource)
	InnerParser.close()

	#create an object of IMGPredator, it will contained a parser of image links of sub pages.
	IMGDownloader = IMGPredator(InnerParser.inner)
	IMGDownloader.fetchback()	#but you just have to call the fetchback() method, all the parsing processes automatically.

Usages:
	run script directly with commandlines:
		-- use default entrance url: sudo python script_name.py
		-- use user-defined entrance url: sudo python script_name.py "http://user-defined/url/here/"
"""

__all__ = ["InnerParser", "IMGLinksProcessor", "IMGPredator"]

from urllib import urlopen, urlretrieve
from sgmllib import SGMLParser
import re
import os
import sys

#Regular prefix of all the inner links.
REGULAR_PREFIX = 'http://tieba.baidu.com'

#Regex for inner links and image links.
HREF_PATTERN = re.compile(r'^/p/\d+$')
IMG_PATTERN = re.compile(r'^http://imgsrc.baidu.com/forum/')

#Entrance url of the traversing.
DEFAULT_TARGET = "http://tieba.baidu.com/f?kw=%B5%B0%CD%B2%D0%A1%BD%E3grapes"
TARGET = len(sys.argv) >= 2 and sys.argv[1] or DEFAULT_TARGET 

class InnerLinksProcessor(SGMLParser):
	"""
	InnerLinksProcessor inherited from SGMLParser, create two new methods:
		start_a(self, attrs) -- called automatically, parsing html tags like: < a href="#"> and restore the value of href.
		output(self) -- if called, it will output all inner links stored in self.inner.

	Meanwhile, reset(self) is a special method automatically called by __init__, which inherited from SGMLParser unvanished.
	"""
	def reset(self):
		SGMLParser.reset(self)
		self.inner = []

	def start_a(self, attrs):
		href = [v for (k, v) in attrs if k == "href" and HREF_PATTERN.search(v)]
		if href:
				self.inner.extend(href)

	def output(self):
		print "Totally parsed %s inner-links in this page:" % len(self.inner)
		for links in self.inner:
				print links

class IMGLinksProcessor(SGMLParser):
	"""
	IMGLinksProcessor inherited from SGMLParser, create two new methods:
		start_img(self, attrs) -- called automatically, parsing html tags like: <img src="#"> and restore the vaule of src.
		output(self) -- if called, it will output all image links stored in self.src.
	
	The reset(self) method called as the description in InnerLinksProcessor doc-string.
	"""
	def reset(self):
		SGMLParser.reset(self)
		self.src = []

	def start_img(self, attrs):
		src = [v for (k, v) in attrs if k == "src" and IMG_PATTERN.match(v)]
		if src:
				self.src.extend(src)
	
	def output(self):
		print "Totally parsed %s img-links in this page:" % len(self.src)
		for links in self.src:
				print links

class IMGPredator:
	"""
	IMGPredator specially designed to fetch back the images of all the image links parsed by IMGLinksProcessor.
	Core Functions:
		_loadIMGTarget(self) -- load a parser of IMGLinksProcessor, travel through all the inner links already
	acquired by InnerLinksProcessor, parsing the image links in the sub pages.
		fetchback(self) -- automatically download the pictures from the image links stored in self.imgTarget,
	renaming them with an ascending integer.
		
	"""
	def __init__(self, innerLinks=None):
		#if innerLinks is given, self.innerTarget will be a list contained by combinations of REGULAR_PREFIX
		#and relative pathname(that is links in innerLinks).otherwise, self.innerTarget will be an empty list.
		self.innerTarget = innerLinks and \
						["%s%s" % (REGULAR_PREFIX, link) for link in innerLinks] or \
						[]

		self.imgTarget = [] #store the final image links, which could be used to download directly.

	def refresh(self):
		"Like the reset method in InnerLinksProcessor and IMGLinksProcessor."
		self.innerTarget = []
		self.imgTarget = []
	
	def close(self):
		self.refresh()

	def _loadIMGTarget(self):
		print "Start parsing image links..."

		IMGParser = IMGLinksProcessor()
		for links in self.innerTarget:
				try:
					sock = urlopen(links)
					htmlSource = sock.read()
				except IOError:
					print "Authentication failed or Internet disconnected, please check your Internet connection..."
				finally:
					sock.close()

				IMGParser.feed(htmlSource)
		IMGParser.close()

		if IMGParser.src:
				print "Parse image links successfully."
				self.imgTarget.extend(IMGParser.src)


	def fetchback(self):
		self._loadIMGTarget()
		
		print "There are %s total images, downloading started..." % len(self.imgTarget)

		auto_ascend = 1
		for links in self.imgTarget:
				try:
					urlretrieve(links, filename = '%s%s' % (auto_ascend, os.path.splitext(links)[1]))
				except IOError:
					print "Authentication failed or Internet disconnected, please check your Internet connection..."
				except Exception as e:
					print "Undefined Error, more descriptions:"
					print "\tError Code:%s\n\tError Info:%s" % (e.errno, e.strerror)

				auto_ascend += 1

		print "Download accomplished."

	def output(self):
		"Mainly designed for testing."
		self._loadIMGTarget()
		print "Totally grabbed %s images:" % len(self.imgTarget)
		for links in self.imgTarget:
				print links

def main():
	InnerParser = InnerLinksProcessor()

	try:
		sock = urlopen(TARGET)
		InnerHTMLSource = sock.read()
	except IOError:
		print "Authentication failed or Internet disconnected, please check your Internet connection..."
	finally:
		sock.close()

	InnerParser.feed(InnerHTMLSource)		
	InnerParser.close()
	IMGDownloader = IMGPredator(InnerParser.inner)
	IMGDownloader.fetchback()
	IMGDownloader.close()


if __name__ == "__main__":
		main()
