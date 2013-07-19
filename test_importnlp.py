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
		pass


	def test_SearchReplace(self):
		INLP = importnlp.ImportNLP('/Users/law826/Desktop/MSK.txt')
		INLP.SearchReplace(INLP.raw, 'fibromas', 'fibroma')
		INLP.SearchReplace(INLP.replaced, 'Fibroma', 'fibroma')
		self.assertEqual(INLP.replaced.count('fibromas'), 0)
		self.assertEqual(INLP.replaced.count('fibroma'), 36)



	def tearDown(self):
		"""
		If this method is defined, the test runner will invoke this after each test. 
		"""
		pass

if __name__ == '__main__':
	unittest.main()
