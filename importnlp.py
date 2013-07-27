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

	def SearchReplace(self, string1, string2):
		"""
		Assign to self.raw a replaced string where string 1 is kept is string 2 is replaced.
		"""
		self.string1 = string1
		self.string2 = string2

		regex = re.compile(r'\b%s\b' % self.string2, re.IGNORECASE)
		self.raw, self.number_replaced = re.subn(regex, string1, self.raw); #print self.eboutput

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
		self.target_body = target_body
		self.target_body = ' ' + self.target_body + ' '

		self.dbrackets = [m.span(1) for m in re.finditer(r"\[([\w \(\)\-]+)\]", target_body, re.IGNORECASE)]
		self.sbrackets = [m.span(1) for m in re.finditer(r"\{([\w \(\)\-]+)\}", target_body, re.IGNORECASE)]
		self.allbrackets = self.dbrackets + self.sbrackets


		def repl(matchobj):
			for span in self.allbrackets:
				if matchobj.start(0) in range(*span):
					return matchobj.group(0)
			return (matchobj.group(1) + self.bracketed_term + matchobj.group(2))	

		for i, term in enumerate(list_of_terms):
			self.bracketed_term = '[' + term + ']'
			if i ==0:
				self.eboutput = re.sub(r"([^\[\w])%s([^\]\w])" %term, repl, self.target_body, re.IGNORECASE); #print self.eboutput
			else:
				self.eboutput = re.sub(r"([^\[\w])%s([^\]\w])" %term, repl, self.eboutput, re.IGNORECASE); #print self.eboutput


	def ExtendCurlys(self, list_of_terms, target_body):
		"""
		Run FindWordsInBracketsAndCurlies first.
		Adds brackets to the same words if they have not yet received brackets.
		"""
		target_body = ' ' + target_body + ' '

		self.dbrackets = [m.span(1) for m in re.finditer(r"\[([\w \(\)\-]+)\]", target_body, re.IGNORECASE)]
		self.sbrackets = [m.span(1) for m in re.finditer(r"\{([\w \(\)\-]+)\}", target_body, re.IGNORECASE)]
		self.allbrackets = self.dbrackets + self.sbrackets

		def repl(matchobj):
			for span in self.allbrackets:
				if matchobj.start(0) in range(*span):
					return matchobj.group(0)			
			return (matchobj.group(1) + self.curly_term + matchobj.group(2))


		for i, term in enumerate(list_of_terms):
			self.curly_term = '{' + term + '}'
			if i ==0:
				self.ecoutput = re.sub(r"([^\{\w])%s([^\}\w])" %term, repl, target_body, re.IGNORECASE); #print self.ecoutput
			else:
				self.ecoutput = re.sub(r"([^\{\w])%s([^\}\w])" %term, repl, self.ecoutput, re.IGNORECASE); #print self.ecoutput


	def ExtendBracketsInFile(self):
		"""
		"""
		self.FindWordsInBracketsAndCurlies(self.raw)
		self.ExtendBrackets(self.diagnoses, self.raw)
		self.ExtendCurlys(self.symptoms, self.eboutput)
		text_file = open(self.file, 'w')
		text_file.write(self.ecoutput)
		text_file.close()

	def FindPictures(self):
		line_array = self.file.readlines()
		for line in line_array:
			diagnoses = [m.group(1) for m in re.finditer(r"\[([\w \(\)\-]+)\]", line)]
			symptoms = [m.group(1) for m in re.finditer(r"\{([\w \(\)\-]+)\}", line)]


if __name__ == '__main__':
	inlp = ImportNLP('/Users/law826/Desktop/MSK (1).txt')
	inlp.ExtendBracketsInFile()

