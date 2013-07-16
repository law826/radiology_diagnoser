#!/usr/bin/env python
# encoding: utf-8
"""
radiology_diagnoser.py

[] handle import file and merging
[] handle old matches from the merge window
[] connect higher order term to everything
[] order symptoms in terms of best algorithm to get to specific diagnosis
[] expand width of windows
[] entry box to merge two nodes in particular
[] figure out brackets
[] edit entry
[] fuzzy search
[] auto update diagnoses and symptoms list upon keystroke (implement fuzzy search)
[] clean up row management
[] make larger entry box
[] make a queue for stored dx and sx
[] make algorithm for stored dx and sx
[] figure out test for multiples for future developement
[] take care of capitalization
[] implement autofill
[] manage database (edit)
[] implement search (real use) of database

Started by LN on 7/4/13
"""
from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *

import basefunctions as bf
import database_for_gui
import mergewindow
import importdata

global searched_term_row
global listbox_row
searched_term_row = 3
listbox_row = 4


class MainWindow:
	def __init__(self):
		self.MakeUI()

	def MakeUI(self):

		self.root = Tk()
		self.root.title("Search")
		self.DB = database_for_gui.DataBaseForGUI(self) # Instantiated here at the end because of parent window issues for ask directory widget.
		self.mw = mergewindow.MergeWindow()
		self.id = importdata.ImportData()
		self.DCWLabelEntryUI(startingrow=0)
		self.LabelEntryUI(startingrow=1)
		self.ResetButton(startingrow=2)
		searched_term_row = 3
		self.SearchedTermUI(startingrow=searched_term_row)
		self.Listboxes()
		self.ButtonsUI(startingrow=6)		
		self.root.mainloop()

	def Listboxes(self):
		listbox_row = 4
		self.DiagnosesListBox(startingrow=listbox_row)
		self.SymptomsListBox(startingrow=listbox_row)


	def DCWLabelEntryUI(self, startingrow):
		# Create a text frame to hold the text Label and the Entry widget
		self.DCWtextFrame = Frame(self.root)		
				
		self.DCWentryLabel = bf.Label(self.DCWtextFrame, "Enter a new diagnosis followed by a comma and then symptoms separated by commas.")
		self.DCWentry = bf.Entry(self.DCWtextFrame, self.DiagnosisCharacterizationSubmitted, completion_list=self.DB.g.vs["name"])

		self.DCWtextFrame.grid(row=startingrow, columnspan=2)

	def DiagnosisCharacterizationSubmitted(self, event=0):
		es_split = bf.ParseEntryCommaSeparated(self.DCWentry, "Enter a diagnosis")
		
		if es_split != []:
			for i, entry in enumerate(es_split):
				if i==0:
					node_index = self.DB.AddNode(entry, "diagnosis")
					node_index_list = []
				else:
					node_index = self.DB.AddNode(entry, "symptom")

				node_index_list.append(node_index)

			node_index_list = self.DB.IndicesOfVertexNeighborsToo(node_index_list)

			self.DB.AddEdges(node_index_list)
			self.UpdateListBox(self.dlistbox, [es_split[0]], row=listbox_row+1, column=0)
			pre_updated_symptom_list = [self.DB.g.vs[x]["name"] for x in node_index_list]
			del pre_updated_symptom_list[0]
			updated_symptom_list = list(set(pre_updated_symptom_list))
			self.UpdateListBox(self.slistbox, updated_symptom_list, row=listbox_row+1, column=1)
			self.DCWentry.delete(0, END)

	def LabelEntryUI(self, startingrow=None):
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)		
				
		self.entryLabel = bf.Label(self.textFrame, "Enter a diagnosis or symptom")
		self.entryWidget = bf.Entry(self.textFrame, self.SearchEntrySubmitted, completion_list=self.DB.g.vs["name"])

		self.textFrame.grid(row=startingrow, columnspan=2)

	
	def ResetButton(self, startingrow=None):
		self.r = Button(self.root, text="Reset", default="normal", command=self.ResetButtonPressed).grid(row=startingrow, columnspan=2)

	def UpdateSearchedTerm(self, startingrow=None):
		startingrow = self.SearchTermUI_startingrow
		try:
			self.searched_term_label.grid_forget()
		except:
			pass
		self.searched_term_label = Label(self.root, text=self.entrystring)
		self.searched_term_label.grid(row=startingrow, columnspan=2)

	def SearchedTermUI(self, startingrow=None):
		self.SearchTermUI_startingrow=startingrow
		self.searched_term_label = Label(self.root, text="")
		self.searched_term_label.grid(row=startingrow, columnspan=2)

	def DiagnosesListBox(self, startingrow=None):	
		self.diagnosisLabel = Label(self.root)
		self.diagnosisLabel["text"] = "Diagnoses"
		self.diagnosisLabel.grid(row=startingrow,column=0)

		self.dlistbox = Listbox(self.root, width=40)
		self.dlistbox.grid(row=startingrow+1,column=0)
		try: 
			for concept in self.DB.g.vs:
				if concept["type"] == 'diagnosis':
					self.dlistbox.insert(END, concept["name"])
		except AttributeError:
		# If there are no items yet.
			pass
		self.dlistbox.bind("<ButtonRelease-1>", self.DiagnosisListPressed)

	def SymptomsListBox(self, startingrow=None):	
		self.symptomsLabel = Label(self.root)
		self.symptomsLabel["text"] = "Symptoms"
		self.symptomsLabel.grid(row=startingrow,column=1)
		self.slistbox = Listbox(self.root, width=40)
		self.slistbox.grid(row=startingrow+1,column=1)
		try: 
			for concept in self.DB.g.vs:
				if concept["type"] == 'symptom':
					self.slistbox.insert(END, concept["name"])
		except AttributeError:
		# If there are no items yet.
			pass

		self.slistbox.bind("<ButtonRelease-1>", self.SymptomListPressed)

	def UpdateListBox(self, listbox, list, row, column):
		listbox.grid_forget()
		listbox.delete(0, END)
		try: 
			for concept in list:
				listbox.insert(END, concept)
		except AttributeError:
		# If there are no items yet.
			pass
		listbox.grid(row=row, column=column)

	def SearchEntrySubmitted(self, event=0, list_clicked=False, selected_concept=None):
		if list_clicked:
			self.entrystring = selected_concept
			dneighbors, sneighbors = self.DB.FindNeighborsOfNode(self.entrystring)
		else:
			if self.entryWidget.get().strip() == "":
				tkMessageBox.showerror("Tkinter Entry Widget", "Enter a term")
			else:
				self.entrystring = self.entryWidget.get().strip()
				dneighbors, sneighbors = self.DB.FindNeighborsOfNode(self.entrystring)
				

		if (dneighbors == None) and (sneighbors == None):
			pass
		else:
			if self.DB.g.vs.find(name=self.entrystring)['type']=='diagnosis':
				dneighbors = [self.entrystring]
			self.UpdateListBox(self.dlistbox, dneighbors, listbox_row+1, 0)
			self.UpdateListBox(self.slistbox, sneighbors, listbox_row+1, 1)
			self.UpdateSearchedTerm(startingrow=searched_term_row)
			self.entryWidget.delete(0, END)

	def ResetButtonPressed(self):
		self.diagnosisLabel.grid_forget()
		self.symptomsLabel.grid_forget()
		self.dlistbox.grid_forget()
		self.slistbox.grid_forget()
		self.Listboxes()

	def DiagnosisListPressed(self, event=0):
		selected_index = self.dlistbox.curselection()
		selected_concept = self.dlistbox.get(selected_index)
		self.SearchEntrySubmitted(list_clicked=True, selected_concept=selected_concept)
		self.ListFocus = "diagnosis"

	def SymptomListPressed(self, event=0):
		selected_index = self.slistbox.curselection()
		selected_concept = self.slistbox.get(selected_index)
		self.SearchEntrySubmitted(list_clicked=True, selected_concept=selected_concept)
		self.ListFocus = "symptom"

	def ButtonsUI(self, startingrow=None):
		self.bottom_buttons_frame = Frame(self.root)
		button_labels = [
			"View Graph",
			"Import",
			"Merge Items",
			"Debug Mode", 
			"Delete Item"
			]

		button_commands = [ 
			self.ViewGraphButtonPressed,
			self.ImportButtonPressed,
			self.MergeButtonPressed,
			self.DebugModeButtonPressed, 
			self.DeleteItem
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.bottom_buttons_frame, text=label, default="normal", command=button_commands[button_number]).pack()

		self.bottom_buttons_frame.grid(row=startingrow, columnspan=2)
	def ViewGraphButtonPressed(self):
		self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
		os.system("open "+self.DB.save_path+os.sep+"graph.svg")

	def ImportButtonPressed(self):
		self.id.executeimport(self)

	def MergeButtonPressed(self):
		self.mw.ExecuteMerge(self)

	def DebugModeButtonPressed(self):
		import pdb; pdb.set_trace()

	def DeleteItem(self):
		selected_concept = self.entrystring
		result = tkMessageBox.askquestion("Delete", "Are you sure you want to delete %s?" %selected_concept, icon='warning')
		if result == 'yes':
			vertex_index = self.DB.g.vs.find(name=selected_concept).index
			self.DB.g.delete_vertices(vertex_index)
			self.DB.SaveGraph()
			self.ResetButtonPressed()
			tkMessageBox.showinfo("Term deleted", "%s has been deleted." %selected_concept)
		else:
			pass

def main():
	
	mainWindow = MainWindow()

if __name__ == '__main__':
    main()


### Utility scripts
## Delete all edges that are loops: STILL NEED TO TEST
# list_to_delete = [x.index for i, x in enumerate(self.DB.g.es) if self.DB.g.is_loop()[i]==True]
# self.DB.g.delete_edges(*list_to_delete)

