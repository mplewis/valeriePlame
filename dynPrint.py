#!/usr/bin/python

import sys

# this code is from http://www.mutaku.com/wp/index.php/2011/06/python-dynamically-printing-to-single-line-of-stdout; thanks!
def dynPrint(data):
	sys.stdout.write("\r\x1b[K"+data.__str__())
	sys.stdout.flush()