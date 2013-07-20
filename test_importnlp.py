from __future__ import division
import importnlp
import unittest
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *


import basefunctions as bf

class TestDatabase(unittest.TestCase):

	def setUp(self):
		self.file_name = '/Users/law826/Desktop/MSK.txt'
		self.INLP = importnlp.ImportNLP('/Users/law826/Desktop/MSK.txt')

	def test_SearchReplace(self):
		self.INLP.SearchReplace(self.INLP.raw, 'fibromas', 'fibroma')
		self.INLP.SearchReplace(self.INLP.replaced, 'Fibroma', 'fibroma')
		self.assertEqual(self.INLP.replaced.count('fibromas'), 0)
		self.assertEqual(self.INLP.replaced.count('fibroma'), 36)

	def test_FindWordsInBracketsAndCurlies(self):
		self.INLP.FindWordsInBracketsAndCurlies(self.INLP.raw)
		#print self.INLP.diagnoses
		#print self.INLP.symptoms

	def test_ExtendBrackets(self):
		list_of_terms = ['fibroma', 'apple']
		target_body = '[fibroma] apple orange'
		self.INLP.ExtendBrackets(list_of_terms, target_body)
		self.assertEqual(self.INLP.eboutput, ' [fibroma] [apple] orange ')

	def test_ExtendCurlys(self):
		list_of_terms = ['fibroma', 'apple']
		target_body = 'fibroma {apple} orange'
		self.INLP.ExtendCurlys(list_of_terms, target_body)
		self.assertEqual(self.INLP.ecoutput, ' {fibroma} {apple} orange ')

	def test_ExtendBracketsInFile(self):
		self.INLP.ExtendBracketsInFile(self.file_name)
		os.system("open " + self.file_name)

	def tearDown(self):
		"""
		If this method is defined, the test runner will invoke this after each test. 
		"""
		pass

if __name__ == '__main__':
	unittest.main()