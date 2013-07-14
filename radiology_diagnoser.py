#!/usr/bin/env python
# encoding: utf-8
"""
radiology_diagnoser.py

[] clean up row management
[] make larger entry box
[] make a queue for stored dx and sx
[] make a reset button
[] make algorithm for stored dx and sx
[] figure out test for multiples for future developement
[] take care of capitalization
[] implement autofill
[] manage database (delete edit)
[] implement search (real use) of database

Started by LN on 7/4/13
"""
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp
from Tkinter import *
from pdb import *
from igraph import *

global searched_term_row
global listbox_row
searched_term_row = 3
listbox_row = 4


class DataBase:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.load_user_settings()
		try:
			self.load_graph()
		except (cPickle.UnpicklingError):
			pass

	def load_user_settings(self):
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

	def load_graph(self):
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
		
		self.save_graph()

				
	def save_graph(self):
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

					# Only add edge if edge doesn't exist and prevent forming loops:
					if first_vertex != second_vertex:
						try:
							self.g.get_eid(first_vertex, second_vertex)
						except InternalError:
							self.g.add_edges((first_vertex, second_vertex))
		self.save_graph()

	def IndicesOfVertexNeighborsToo(self, node_index_list):
		"""
		Connect a symptom with the rest of the symptoms under a diagnosis.
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

class MainWindow:
	def __init__(self):
		self.DB = DataBase(self) # Instantiated here at the end because of parent window issues for ask directory widget.
		self.MakeUI()

	def MakeUI(self):

		self.root = Tk()
		self.root.title("Search")
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
				
		# Create a Label in DCWtextFrame
		self.DCWentryLabel = Label(self.DCWtextFrame)
		self.DCWentryLabel["text"] = "Enter new diagnosis: followed by symptoms separated by commas"
		self.DCWentryLabel.pack()
	
		# Create an Entry Widget in DCWtextFrame
		self.DCWentryWidget = tkcomp.AutocompleteEntry(self.DCWtextFrame)
		self.DCWentryWidget.set_completion_list(self.DB.g.vs["name"])
		self.DCWentryWidget["width"] = 50
		self.DCWentryWidget.pack()
		self.DCWentryWidget.focus_set()
		self.DCWentryWidget.bind("<Return>", self.DiagnosisCharacterizationSubmitted)
		self.DCWtextFrame.grid(row=startingrow, columnspan=2)

	def DiagnosisCharacterizationSubmitted(self, event=0):
		if self.DCWentryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a diagnosis")
		else:
			DCWentrystring = self.DCWentryWidget.get().strip()
			es_split_pre = DCWentrystring.split(",")
			es_split = [x.lstrip() for x in es_split_pre]

			
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
			self.DCWentryWidget.delete(0, END)


		# 	self.DB.AddNode(self.entryWidget.get().strip())
		# 	self.DB.save_graph()
		# 	tkMessageBox.showinfo("Confirmation", "%s has been added." % self.entryWidget.get().strip())
		# 	self.entryWidget.delete(0, END)	
		# self.SetGraphStatistics()
		# self.entryWidget.focus_set()

	def LabelEntryUI(self, startingrow=None):
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)		
				
		# Create a Label in textFrame
		self.entryLabel = Label(self.textFrame)
		self.entryLabel["text"] = "Enter a diagnosis or symptom"
		self.entryLabel.pack()
	
		# Create an Entry Widget in textFrame
		self.entryWidget = tkcomp.AutocompleteEntry(self.textFrame)
		self.entryWidget.set_completion_list(self.DB.g.vs["name"])
		self.entryWidget["width"] = 50
		self.entryWidget.pack()
		self.entryWidget.focus_set()
		self.entryWidget.bind("<Return>", self.SearchEntrySubmitted)
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

	def SymptomListPressed(self, event=0):
		selected_index = self.slistbox.curselection()
		selected_concept = self.slistbox.get(selected_index)
		self.SearchEntrySubmitted(list_clicked=True, selected_concept=selected_concept)

	def ButtonsUI(self, startingrow=None):
		self.bottom_buttons_frame = Frame(self.root)
		button_labels = [
			'Manage Database',
			"View Graph",
			"Import",
			"Debug Mode"
			]

		button_commands = [ 
			self.ManageDatabaseButtonPressed,
			self.ViewGraphButtonPressed,
			self.ImportButtonPressed,
			self.DebugModeButtonPressed
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.bottom_buttons_frame, text=label, default="normal", command=button_commands[button_number]).pack()

		self.bottom_buttons_frame.grid(row=startingrow, columnspan=2)

	def ManageDatabaseButtonPressed(self):
		ManageDatabaseWindow(self)

	def ViewGraphButtonPressed(self):
		self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
		os.system("open "+"/Users/law826/github/radiology_diagnoser/graph.svg")

	def ImportButtonPressed(self):
		importdata = ImportData(self)

	def DebugModeButtonPressed(self):
		import pdb; pdb.set_trace()

class ManageDatabaseWindow:
	def __init__(self, mainwindow):

		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.root = Tk()
		self.root.title("Database Manager")
		self.MakeListBox()
		mainloop()

	def MakeListBox(self):	
		self.listbox = Listbox(self.root)
		self.listbox.pack()
		self.b = Button(self.root, text = "Delete", command = self.DeleteItem)
		self.b.pack()
		try: 
			for concept in self.DB.g.vs["name"]:
				self.listbox.insert(END, concept)
		except AttributeError:
		# If there are no items yet.
			pass


	def DeleteItem(self):
		selected_index = self.listbox.curselection()
		selected_concept = self.listbox.get(selected_index)

		result = tkMessageBox.askquestion("Delete", "Are you sure you want to delete %s?" %selected_concept, icon='warning')
		if result == 'yes':
			vertex_index = self.DB.g.vs.find(name=selected_concept).index
			self.DB.g.delete_vertices(vertex_index)
			self.listbox.pack_forget()
			self.b.pack_forget()
			self.MakeListBox()
			self.DB.save_graph()
			tkMessageBox.showinfo("Term deleted", "%s has been deleted." %selected_concept)
		else:
			pass

class ImportData:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		#self.import_file = tkFileDialog.askopenfile(parent = self.mainwindow.root, title = 'Please choose a file to import')
		self.import_file = open('/Users/law826/Downloads/MSK.txt')
		line_array = self.import_file_readlines()

		for line in line_array:
			diagnosis = line_array[0][line_array[0].find("[")+1:line_array[0].find("]")]
			symptom = line_array[0][line_array[0].find("{")+1:line_array[0].find("}")]



		import pdb; pdb.set_trace()










def main():
	
	mainWindow = MainWindow()

if __name__ == '__main__':
    main()


### Utility scripts
## Delete all edges that are loops: STILL NEED TO TEST
# list_to_delete = [x.index for i, x in enumerate(self.DB.g.es) if self.DB.g.is_loop()[i]==True]
# self.DB.g.delete_edges(*list_to_delete)

