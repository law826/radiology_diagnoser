#!/usr/bin/env python
# encoding: utf-8
"""
radiology_diagnoser.py

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

global searched_term_row
global listbox_row
searched_term_row = 3
listbox_row = 4


class DataBase:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.LoadUserSettings()
		try:
			self.LoadGraph()
		except (cPickle.UnpicklingError):
			pass

	def LoadUserSettings(self):
		try: 
			self.user_settings = cPickle.load(open('user_settings.p', 'rb'))
			if os.getcwd() in self.user_settings:
				self.save_path = self.user_settings[os.getcwd()]
			else:
				tkMessageBox.showinfo("New User/Computer Detected. Please choose a save directory.")	
				self.SetPath()
		except (IOError, cPickle.UnpicklingError):
			self.user_settings = dict()
			tkMessageBox.showinfo("New User/Computer Detected", "Please choose a save directory.")
			self.SetPath()

	def LoadGraph(self):
		self.g = Graph.Read_Pickle(os.sep.join([self.save_path, "graph.p"]))

	def AddNode(self, item, type):
		try:
			self.g
		except AttributeError:
			self.g = Graph()
			self.g.add_vertices(1)
			self.g.es["weight"] = 1.0
			self.g["name"] = "Ideas Graph"			
			self.g.vs[0]["name"] = item
			self.g.vs[0]["type"] = type

			return 0
		else:
			try:
				"""
				If node already exists, then add edges to existing node.

				"""
				node_index = self.g.vs.find(name=item).index
				return node_index
			except ValueError:
				"""
				Do this if node does not already exist.
				"""
				self.g.add_vertices(1)
				number_of_vertices = self.g.vcount()
				self.g.vs[number_of_vertices-1]["name"] = item
				self.g.vs[number_of_vertices-1]["type"] = type

				return number_of_vertices-1 #This is the node's index.
		
		self.SaveGraph()
				
	def SaveGraph(self):
		try:
			self.g.write_pickle(os.sep.join([self.save_path, "graph.p"]))
		except:
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a valid save path (current path is %s)" %self.save_path)

	def AddEdges(self, node_index_list):
		"""
		Add combinations of all nodes given a list of the nodes' indices.

		"""
		for first_index_counter, first_vertex in enumerate(node_index_list):
			for second_vertex_counter in range((len(node_index_list)-1)):
				second_index = first_index_counter+second_vertex_counter+1
				if second_index <= (len(node_index_list)-1):
					second_vertex = node_index_list[second_index]

					# Only add edge if edge doesn't exist (prevent multiples) and prevent forming loops:
					if first_vertex != second_vertex:
						try:
							self.g.get_eid(first_vertex, second_vertex)
						except InternalError:
							self.g.add_edges((first_vertex, second_vertex))
		self.SaveGraph()

	def IndicesOfVertexNeighborsToo(self, node_index_list):
		"""
		Take a list of node indices and connect a symptom with the rest of the symptoms under a diagnosis.
		"""
		diagnosis_vertex=self.g.vs[node_index_list[0]]
		neighbor_list = [x.index for x in diagnosis_vertex.neighbors()]
		merged_index_list = node_index_list + neighbor_list

		return merged_index_list

	def FindNeighborsOfNode(self, nodename):
		"""
		Take the name of a node and returns a list of the names of the neighboring nodes of type diagnosis and of type symptom. 
		"""
		try:
			node = self.g.vs.find(name=nodename)
		except (NameError, ValueError):
			tkMessageBox.showinfo("Term Not Found", "%s is not in the database" % entrystring)

		dneighbors = [x["name"] for x in node.neighbors() if x["type"]=="diagnosis"]
		sneighbors = [x["name"] for x in node.neighbors() if x["type"]=="symptom"]

		return dneighbors, sneighbors

	def SetPath(self):
		self.save_path = tkFileDialog.askdirectory(parent = self.mainwindow.root, title = 'Please choose a save directory')
		self.user_settings[os.getcwd()] = self.save_path
		cPickle.dump(self.user_settings, open('user_settings.p', 'wb'))	

	def IdentifySimilarNodes(self, inlist, threshold=0.25):
		"""
		Take a list of items and identifies similar nodes based upon Levenshtein distance.
		Returns a list of tuples of similar items.
		"""
		tuple_combos = [(x,y) for x in inlist for y in inlist if x!=y]
		similar_nodes_tuples = []
		for entry in tuple_combos:
			if (entry[1], entry[0]) in tuple_combos:
				tuple_combos.remove((entry[1], entry[0])) 

			total_length = len(entry[0]) + len(entry[0])
			normed_LD = (nltk.metrics.edit_distance(*entry))/total_length

			if normed_LD < threshold:
				similar_nodes_tuples.append(entry)

		return similar_nodes_tuples

	def MergeNodes(self, nodename1, nodename2):
		"""
		Merge two nodes such that node1 is the remaining node and inherits all of the edges of node 2.
		"""

		# Find neighbors of node 2.
		dneighbors, sneighbors = self.FindNeighborsOfNode(nodename2)
		everyone = dneighbors+sneighbors+[nodename1]

		everyone_indices = [self.g.vs.find(name=nodename).index for nodename in everyone]
		
		# Make edges from node 2 to node 1.
		self.AddEdges(everyone_indices)

		# Delete node 2.
		self.g.delete_vertices(self.g.vs.find(name=nodename2).index)

		"""
		Query whether a merge should take place and 
		"""

class MainWindow:
	def __init__(self):
		self.MakeUI()

	def MakeUI(self):

		self.root = Tk()
		self.root.title("Search")
		self.DB = DataBase(self) # Instantiated here at the end because of parent window issues for ask directory widget.
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
		set_trace()
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
		self.DCWentry = bf.Entry(self.textFrame, self.SearchEntrySubmitted, completion_list=self.DB.g.vs["name"])

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
		else:
			if self.entryWidget.get().strip() == "":
				tkMessageBox.showerror("Tkinter Entry Widget", "Enter a diagnosis")
			else:
				self.entrystring = self.entryWidget.get().strip()
		dneighbors, sneighbors = self.DB.FindNeighborsOfNode(self.entrystring)

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
		importdata = ImportData(self)

	def MergeButtonPressed(self):
		mergewindow = MergeWindow(self)

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

class ImportData:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.DB = mainwindow.DB
		#self.import_file = tkFileDialog.askopenfile(parent = self.mainwindow.root, title = 'Please choose a file to import')
		self.import_file = open('/Users/law826/Downloads/MSK.txt')
		line_array = self.import_file.readlines()
		for line in line_array:
			diagnoses = [m.group(1) for m in re.finditer(r"\[([A-Za-z0-9_ \(\)]+)\]", line)]
			symptoms = [m.group(1) for m in re.finditer(r"\{([A-Za-z0-9_ \(\)]+)\}", line)]

			for diagnosis in diagnoses:
				node_index_list=[]
				node_index = self.DB.AddNode(diagnosis, "diagnosis")
				node_index_list.append(node_index)
				for symptom in symptoms:
					node_index = self.DB.AddNode(symptom, "symptom")
					node_index_list.append(node_index)
				self.DB.AddEdges(node_index_list)

		self.DB.SaveGraph()
		self.mainwindow.ResetButtonPressed()


class MergeWindow:
	def __init__(self, mainwindow):
		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.root = Tk()
		self.root.title("Merge Items")
		self.MergeInputBox()
		self.MakeListBox()
		mainloop()

	def MergeInputBox(self):
		# Create a Label in textFrame
		self.textFrame = Frame(self.root)

		self.entryLabel = bf.Label(self.textFrame, "Enter terms to merge, separated by commas (keep first term)")
		self.entry = Entry(self.textFrame, MergeInputBoxSubmitted, completion_list=self.DB.g.vs["name"])

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
		es_split = bf.ParseEntryCommaSeparated(self.entryWidget, "Please Enter Items to Merge")
		print es_split
		return es_split

	def MergeButtonPressed(self, button_index):
		selected_index = self.listbox.curselection()
		selected_concept = self.listbox.get(selected_index)
		
		result = tkMessageBox.askquestion("Merge", "Are you sure you want to merge '%s' and '%s'?" %(selected_concept[0], selected_concept[1]), icon='warning')
		if result == 'yes':
			if button_index==0:
				self.DB.MergeNodes(selected_concept[0], selected_concept[1])
				kept_node = selected_concept[0]
			elif button_index == 1:
				self.DB.MergeNodes(selected_concept[1], selected_concept[0])
				kept_node = selected_concept[1]

			self.listbox.pack_forget()
			self.b0.pack_forget()
			self.b1.pack_forget()
			self.MakeListBox()
			self.DB.SaveGraph()
			tkMessageBox.showinfo("Merged", "'%s' and '%s' have been merged, keeping '%s'." %(selected_concept[0], selected_concept[1], kept_node))
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

