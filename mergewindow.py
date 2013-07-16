from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *

import basefunctions as bf

class MergeWindow:
	def __init__(self):
		pass

	def ExecuteMerge(self, mainwindow):
		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.id = mainwindow.id
		self.root = Tk()
		self.root.title("Merge Items")
		self.MergeInputBox()
		self.MakeListBox()
		mainloop()

	def MergeInputBox(self):
		# Create a Label in textFrame
		self.textFrame = Frame(self.root)

		self.entryLabel = bf.Label(self.textFrame, "Enter terms to merge, separated by commas (keep first term)")
		self.mentryWidget = bf.Entry(self.textFrame, self.MergeInputBoxSubmitted, completion_list=self.DB.g.vs["name"])

		self.textFrame.pack()

	def MakeListBox(self):	
		self.listbox = Listbox(self.root, width=80)
		self.listbox.pack()
		self.buttonFrame = Frame(self.root)
		self.b0 = Button(self.buttonFrame, text = "Keep First: Merge Second", command = lambda: self.MergeButtonPressed(0))
		self.b0.pack(side = LEFT)
		self.b1 = Button(self.buttonFrame, text = "Keep Second: Merge First", command = lambda: self.MergeButtonPressed(1))
		self.b1.pack(side = LEFT)

		self.buttonFrame.pack()
		self.similar_node_tuples = self.DB.IdentifySimilarNodes(self.DB.g.vs["name"], threshold=0.25)
		try: 
			for pair in self.similar_node_tuples:
				self.listbox.insert(END, pair)
		except AttributeError:
		# If there are no items yet.
			pass

	def MergeInputBoxSubmitted(self, event=0):
		es_split = bf.ParseEntryCommaSeparated(self.mentryWidget, "Please Enter Items to Merge")
		print es_split
		return es_split

	def MergeButtonPressed(self, button_index):
		selected_index = self.listbox.curselection()
		selected_concept = self.listbox.get(selected_index)
		
		result = tkMessageBox.askquestion("Merge", "Are you sure you want to merge '%s' and '%s'?" %(selected_concept[0], selected_concept[1]), icon='warning')
		if result == 'yes':
			if button_index==0:
				self.DB.MergeNodes(selected_concept[0], selected_concept[1])
				self.kept_node = selected_concept[0]
				self.deleted_node = selected_concept[1]

			elif button_index == 1:
				self.DB.MergeNodes(selected_concept[1], selected_concept[0])
				self.kept_node = selected_concept[1]
				self.deleted_node = selected_concept[0]

			self.listbox.pack_forget()
			self.b0.pack_forget()
			self.b1.pack_forget()
			self.MakeListBox()
			self.DB.SaveGraph()
			tkMessageBox.showinfo("Merged", "'%s' and '%s' have been merged, keeping '%s'." %(selected_concept[0], selected_concept[1], self.kept_node))
			self.id.SearchReplaceImportFile()
		else:
			pass
