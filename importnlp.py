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

	def FindWordsInBracketsAndCurlies(self, body):
		"""
		Returns words without brackets in self.diagnoses and self.symptoms.
		"""
		self.diagnoses = [m.group(1) for m in re.finditer(r"\[([A-Za-z0-9_ \(\)\-]+)\]", body)]
		self.symptoms = [m.group(1) for m in re.finditer(r"\{([A-Za-z0-9_ \(\)\-]+)\}", body)]

	def ExtendBrackets(self, list_of_terms, target_body):
		"""
		Run FindWordsInBracketsAndCurlies first.
		Adds brackets to the same words if they have not yet received brackets.
		"""
		target_body = ' ' + target_body + ' '

		for i, term in enumerate(list_of_terms):
			bracketed_term = ' [' + term + '] '
			if i ==0:
				self.eboutput = re.sub(r"[^[]%s[^]]" %term, bracketed_term, target_body); #print self.eboutput
			else:
				self.eboutput = re.sub(r"[^[]%s[^]]" %term, bracketed_term, self.eboutput); #print self.eboutput

	def ExtendCurlys(self, list_of_terms, target_body):
		"""
		Run FindWordsInBracketsAndCurlies first.
		Adds brackets to the same words if they have not yet received brackets.
		"""
		target_body = ' ' + target_body + ' '


		for i, term in enumerate(list_of_terms):
			curly_term = ' {' + term + '} '
			if i ==0:
				self.ecoutput = re.sub(r"[^{]%s[^}]" %term, curly_term, target_body); #print self.ecoutput
			else:
				self.ecoutput = re.sub(r"[^{]%s[^}]" %term, curly_term, self.ecoutput); #print self.ecoutput


	def ExtendBracketsInFile(self, file_name):
		"""
		"""
		self.FindWordsInBracketsAndCurlies(self.raw)
		self.ExtendBrackets(self.diagnoses, self.raw)
		self.ExtendCurlys(self.symptoms, self.eboutput)
		text_file = open(file_name, 'w')
		text_file.write(self.ecoutput)
		text_file.close()


