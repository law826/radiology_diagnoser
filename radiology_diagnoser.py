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
from PIL import Image, ImageTk

import basefunctions as bf
import database_for_gui
import mergewindow
import importdata
sys.path.append(os.path.realpath('./SearchReplace'))
from SearchReplaceGUI import SearchReplaceGUI
from SearchReplaceGUI import SaveData


class MainWindow:
	def __init__(self):
		# Establishment of GUI
		self.root = Tk()
		self.root.title("Search")

		# Instantiation of other modules.
		self.DB = database_for_gui.DataBaseForGUI(self) # Instantiated here at the end because of parent window issues for ask directory widget.
		self.mw = mergewindow.MergeWindow()
		self.id = importdata.ImportData()
		self.srg = SearchReplaceGUI()

		gui_elements = [self.LabelEntryUI,
						self.ResetButton,
						self.SearchedTermUI,
						self.Listboxes,
						self.ButtonsUI,
						self.RadiographUI
		]

		self.gui_element_dict = {}

		for startingrow, gui_element in enumerate(gui_elements):
			self.gui_element_dict[gui_element] = startingrow
			gui_element(startingrow=startingrow)

		self.root.mainloop()

	def Listboxes(self, startingrow):
		self.DiagnosesListBox(startingrow=startingrow)
		self.SymptomsListBox(startingrow=startingrow)

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
		self.lbframe = Frame(self.root)
		self.lbframe.grid(row = startingrow, columnspan = 2)
		self.diagnosisLabel = Label(self.lbframe)
		self.diagnosisLabel["text"] = "Diagnoses"
		self.diagnosisLabel.grid(row=0,column=0)
		self.dlistbox = Listbox(self.lbframe, width=40, selectmode=EXTENDED)
		self.dfunc_id = self.dlistbox.bind("<ButtonRelease-1>", self.DiagnosisListPressed)
			
		self.dlistbox.grid(row=1,column=0)

		try: 
			sorted_list = self.DB.g.vs['name']
			sorted_list.sort(lambda x, y:cmp(x.lower(),y.lower()))
			for concept in sorted_list:
				vertex = self.DB.g.vs.find(name=concept)
				if vertex["type"] == 'diagnosis':
					self.dlistbox.insert(END, concept)
		except AttributeError:
		# If there are no items yet.
			pass

	def SymptomsListBox(self, startingrow=None):	
		self.symptomsLabel = Label(self.lbframe)
		self.symptomsLabel["text"] = "Symptoms"
		self.symptomsLabel.grid(row=0,column=1)
		self.slistbox = Listbox(self.lbframe, width=40, selectmode=EXTENDED)
		self.sfunc_id = self.slistbox.bind("<ButtonRelease-1>", self.SymptomListPressed)

		self.slistbox.grid(row=1,column=1)

		try: 
			sorted_list = self.DB.g.vs['name']
			sorted_list.sort(lambda x, y:cmp(x.lower(),y.lower()))
			for concept in sorted_list:
				vertex = self.DB.g.vs.find(name=concept)
				if vertex["type"] == 'symptom':
					self.slistbox.insert(END, concept)
		except AttributeError:
		# If there are no items yet.
			pass

	def UpdateListBox(self, listbox, list, row, column):
		listbox.grid_forget()
		listbox.delete(0, END)
		try: 
			sorted_list = list
			sorted_list.sort(lambda x, y:cmp(x.lower(),y.lower()))
			for concept in sorted_list:
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
			self.UpdateListBox(self.dlistbox, dneighbors, 1, 0)
			self.UpdateListBox(self.slistbox, sneighbors, 1, 1)
			self.UpdateSearchedTerm(startingrow=self.gui_element_dict[self.SearchedTermUI])
			self.entryWidget.delete(0, END)

	def ResetButtonPressed(self):
		self.diagnosisLabel.grid_forget()
		self.symptomsLabel.grid_forget()
		self.dlistbox.grid_forget()
		self.slistbox.grid_forget()
		self.Listboxes(self.gui_element_dict[self.Listboxes])

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
			"Add Diagnosis",
			"Import",
			"SearchReplaceGUI",
			"Merge Items",
			"Debug Mode", 
			"Delete Item"
			]

		button_commands = [ 
			self.AddDiagnosisButtonPressed,
			self.ImportButtonPressed,
			self.SearchReplaceGUIButtonPressed,
			self.MergeButtonPressed,
			self.DebugModeButtonPressed, 
			self.DeleteItem
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.bottom_buttons_frame, text=label, default="normal", command=button_commands[button_number]).pack(side = LEFT)

		self.bottom_buttons_frame.grid(row=startingrow, columnspan=2)

	def RadiographUI(self, startingrow):
		self.radframe = Frame(self.root)
		self.radframe.grid(row = startingrow, columnspan = 2)

		image = Image.open('/Users/law826/Desktop/test.jpg')
		photo = ImageTk.PhotoImage(image)
		radiograph = Label(self.radframe, image=photo)
		radiograph.image = photo
		radiograph.pack()

		caption = Label(self.radframe)
		caption["text"] = "this is a test caption"
		caption.pack()



	def AddDiagnosisButtonPressed(self):
		dcw = DiagnosisCharWin(self)

	# def ViewGraphButtonPressed(self):
	# 	self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
	# 	os.system("open "+self.DB.save_path+os.sep+"graph.svg")

	def ImportButtonPressed(self):
		self.id.executeimport(self)

	def SearchReplaceGUIButtonPressed(self):
		self.srg.main()

	def MergeButtonPressed(self):
		self.dlistbox.unbind("<ButtonRelease-1>", self.dfunc_id)
		self.slistbox.unbind("<ButtonRelease-1>", self.sfunc_id)
		self.bottom_buttons_frame.grid_forget()

		self.mbuttons_frame = Frame(self.root)
		self.mbuttons_frame.grid(row=self.gui_element_dict[self.ButtonsUI], columnspan=2)

		button_labels = [
			"Merge Selected Items",
			"Exit Merge Mode"
			]

		button_commands = [  
			self.MergeSelectedItems,
			self.ExitButtonPressed,
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.mbuttons_frame, text=label, default="normal", command=button_commands[button_number]).pack(side = LEFT)
		
	def MergeSelectedItems(self):
		selected_indices = self.dlistbox.curselection()
		list_chosen = 'diagnoses'
		if selected_indices == ():
			selected_indices = self.slistbox.curselection()
			list_chosen = 'symptoms'
		if len(selected_indices) != 2:
			tkMessageBox.showerror("Tkinter Entry Widget", "Please select two items to merge")
			return

		if list_chosen == 'diagnoses':
			self.merge_items = [self.dlistbox.get(selected_index) for selected_index in selected_indices]
		elif list_chosen == 'symptoms':
			self.merge_items = [self.slistbox.get(selected_index) for selected_index in selected_indices]



		result = tkMessageBox.askquestion("Delete", "Press yes to keep %s and press no to keep %s" %(self.merge_items[0], self.merge_items[1]), icon='warning')
		if result == 'yes':
			pass
		else:
			self.merge_items.reverse()

		# At this point self.merge_items will the item to keep in first position and the one to delete in second position.

		# Confirm merge
		result = tkMessageBox.askquestion("Delete", "Are you sure you want to keep %s and merge %s? Press yes to continue." %(self.merge_items[0], self.merge_items[1]), icon='warning')
		if result == 'yes':
			self.DB.MergeNodes(self.merge_items[0], self.merge_items[1]) 
			self.DB.SaveGraph()
			tkMessageBox.showinfo("Merged", "'%s' and '%s' have been merged, keeping '%s'." %(self.merge_items[0], self.merge_items[1], self.merge_items[0]))
			self.ResetButtonPressed()

			# Make modifications to import NLP pickle.
			self.srg.sd.replacement_tuples.append(tuple(self.merge_items))
			self.srg.sd.Save()

		else:
			return


		


		

	def ExitButtonPressed(self):
		self.mbuttons_frame.grid_forget()
		self.ButtonsUI(startingrow=self.gui_element_dict[self.ButtonsUI])
		self.dfunc_id = self.dlistbox.bind("<ButtonRelease-1>", self.DiagnosisListPressed)
		self.sfunc_id = self.slistbox.bind("<ButtonRelease-1>", self.SymptomListPressed)
		# self.mw.ExecuteMerge(self)

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


class DiagnosisCharWin:
	def __init__(self, mainwindow):
		self.mw = mainwindow
		self.DB = mainwindow.DB
		self.root = Tk()
		self.root.title("Characterize a diagnosis")
		self.DCWtextFrame = Frame(self.root)			
		self.DCWentryLabel = bf.Label(self.DCWtextFrame, "Enter a new diagnosis followed by a comma and then symptoms separated by commas.")
		self.DCWentry = bf.Entry(self.DCWtextFrame, self.DiagnosisCharacterizationSubmitted, completion_list=self.DB.g.vs["name"])
		self.DCWtextFrame.grid(row=0, column=0)
		self.root.mainloop()

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
			self.mw.UpdateListBox(self.mw.dlistbox, [es_split[0]], row=1, column=0)
			pre_updated_symptom_list = [self.DB.g.vs[x]["name"] for x in node_index_list]
			del pre_updated_symptom_list[0]
			updated_symptom_list = list(set(pre_updated_symptom_list))
			self.mw.UpdateListBox(self.mw.slistbox, updated_symptom_list, row=1, column=1)
			self.DCWentry.delete(0, END)

def main():
	
	mainWindow = MainWindow()

if __name__ == '__main__':
    main()


### Utility scripts
## Delete all edges that are loops: STILL NEED TO TEST
# list_to_delete = [x.index for i, x in enumerate(self.DB.g.es) if self.DB.g.is_loop()[i]==True]
# self.DB.g.delete_edges(*list_to_delete)

