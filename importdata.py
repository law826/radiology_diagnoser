from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *

import basefunctions as bf

class ImportData:
	def __init__(self):

		self.import_file = open('/Users/law826/Desktop/MSK (1).txt', 'r')

	def executeimport(self, mainwindow):
		self.mainwindow = mainwindow
		self.DB = mainwindow.DB
		self.mw = mainwindow.mw
		#self.import_file = tkFileDialog.askopenfile(parent = self.mainwindow.root, title = 'Please choose a file to import')
		
		line_array = self.import_file.readlines()
		for line in line_array:
			diagnoses = [m.group(1) for m in re.finditer(r"\[([A-Za-z0-9_ \(\)\-]+)\]", line)]
			symptoms = [m.group(1) for m in re.finditer(r"\{([A-Za-z0-9_ \(\)\-]+)\}", line)]

			for diagnosis in diagnoses:
				node_index_list=[]
				node_index = self.DB.AddNode(diagnosis, "diagnosis")
				node_index_list.append(node_index)
				for symptom in symptoms:
					node_index = self.DB.AddNode(symptom, "symptom")
					node_index_list.append(node_index)
				self.DB.AddEdges(node_index_list)

		self.DB.SaveGraph()
		self.SearchReplaceImportFile()
		self.mainwindow.ResetButtonPressed()

	def SearchReplaceImportFile(self):
		for line in self.import_file:
			self.import_file.write(line.replace(self.mw.deleted_node, self.mw.kept_node))



