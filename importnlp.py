from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *


import basefunctions as bf
import nltk

class ImportNLP:
	def __init__(self, file):
		self.file = file
		self.f = open(self.file, 'r')
		self.raw = self.f.read()

	def SearchReplace(self, body, string1, string2):
		self.string1 = string1
		self.string2 = string2
		self.replaced = body.replace(self.string1, self.string2)

	def FindWordsInBrackets(self, body):
		self.diagnoses = [m.group(1) for m in re.finditer(r"\[([A-Za-z0-9_ \(\)\-]+)\]", body)]
		self.symptoms = [m.group(1) for m in re.finditer(r"\{([A-Za-z0-9_ \(\)\-]+)\}", body)]

	def ExtendBrackets(self, list_of_terms, target_body, file=None):
		"""
		Adds brackets to the same words if they have not yet received brackets.
		"""

		target_body = ' ' + target_body + ' '

		for i, term in enumerate(list_of_terms):
			bracketed_term = ' [' + term + '] '
			if i ==0:
				self.eboutput = re.sub(r"[^[]%s[^]]" %term, bracketed_term, target_body); print self.eboutput
			else:
				self.eboutput = re.sub(r"[^[]%s[^]]" %term, bracketed_term, self.eboutput); print self.eboutput



		# Open a file for reading and another for writing.
		

		# _fibromas = re.compile('are')
		# #match = _fibromas.finditer(self.raw)
		# set_trace()
		# [m.group(1) for m in re.finditer(_fibromas, self.raw)]
		
		# set_trace()
		
		
		# Take two words and replace all instances of that the second word with the first word.


		# Store this store this replace for future mappings.
		# Apply previous search and replace mappings from a save file.


