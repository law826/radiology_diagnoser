from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *


import basefunctions as bf
import nltk

class ImportNLP:
	def __init__(self, file, string1, string2):
		self.file = file
		self.string1 = string1
		self.string2 = string2
		pass

	def main(self):

		# Open a file for reading and another for writing.
		self.f = open(self.file, 'r')
		self.raw = self.f.read()

		_fibromas = re.compile('a')
		#match = _fibromas.finditer(self.raw)
		
		[m.group(1) for m in re.finditer(_fibromas, self.raw)]
		
		set_trace()
		
		
		# Take two words and replace all instances of that the second word with the first word.


		# Store this store this replace for future mappings.
		# Apply previous search and replace mappings from a save file.


