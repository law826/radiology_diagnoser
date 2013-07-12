#!/usr/bin/env python
# encoding: utf-8
"""
radiology_diagnoser.py

Started by LN on 7/4/13
"""
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp
from Tkinter import *
from pdb import *
import igraph



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
		self.g = igraph.Graph.Read_Pickle(os.sep.join([self.save_path, "graph.p"]))


	def append_to_graph(self, item, type):
		try:
			self.g
		except AttributeError:
			self.g = igraph.Graph()
			self.g.add_vertices(1)
			self.g.es["weight"] = 1.0
			self.g["name"] = "Ideas Graph"			
			self.g.vs[0]["name"] = item
			self.g.vs[0]["type"] = type
		else:
			self.g.add_vertices(1)
			number_of_vertices = self.g.vcount()
			self.g.vs[number_of_vertices-1]["name"] = item
			self.g.vs[number_of_vertices-1]["type"] = types
		self.save_graph()

				
	def save_graph(self):
		try:
			self.g.write_pickle(os.sep.join([self.save_path, "graph.p"]))
		except:
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a valid save path (current path is %s)" %self.save_path)

	def AddEdges(self, len_latest):
		self.len_latest = len_latest
		number_of_vertices = self.g.vcount()
		for 
		self.list_of_edges = 

		pass

	def SetPath(self):
		self.save_path = tkFileDialog.askdirectory(parent = self.mainwindow.root, title = 'Please choose a save directory')
		self.user_settings[os.getcwd()] = self.save_path
		cPickle.dump(self.user_settings, open('user_settings.p', 'wb'))		


class MainWindow:
	def __init__(self):

		self.MakeUI()
			
	def MakeUI(self):
		self.root = Tk()
		self.root.title("Please give a rating")

		self.ButtonsUI()

		self.DB = DataBase(self) # Instantiated here at the end because of parent window issues for ask directory widget.
		self.root.mainloop()

	def ButtonsUI(self):
		button_labels = [
			'Add Diagnosis', 
			]

		button_commands = [
			self.AddDiagnosisButtonPressed
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.root, text=label, default="normal", command=button_commands[button_number]).pack()

	def AddDiagnosisButtonPressed(self):
		DiagnosisCharterizationWindow(self)

	def SetPath(self):
		self.DB.save_path = tkFileDialog.askdirectory(title = 'Please choose a save directory')

class DiagnosisCharterizationWindow:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.DB = mainwindow.DB
		self.MakeUI()

	def MakeUI(self):
		self.root = Tk()
		self.root.title("Diagnosis")


		self.LabelEntryUI()
		self.AddButton()

		self.root.mainloop()

	def LabelEntryUI(self):
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)		
				
		# Create a Label in textFrame
		self.entryLabel = Label(self.textFrame)
		self.entryLabel["text"] = "Enter the diagnosis: followed by symptoms separated by commas"
		self.entryLabel.pack(side=LEFT)
	
		# Create an Entry Widget in textFrame
		self.entryWidget = tkcomp.AutocompleteEntry(self.textFrame)
		self.entryWidget.set_completion_list(['test', 'test2', 'list2'])
		self.entryWidget["width"] = 50
		self.entryWidget.pack(side=LEFT)
		self.entryWidget.focus_set()
		self.entryWidget.bind("<Return>", self.AddButtonPressed)
		self.textFrame.pack()

	def AddButton(self):
		self.b = Button(self.root, text="Add Diagnosis", default="normal", command=self.AddButtonPressed).pack()

	def AddButtonPressed(self, event=0):
		if self.entryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a diagnosis")
		else:			
			entrystring = self.entryWidget.get().strip()
			es_split = entrystring.split(",")
			
			for i, entry in enumerate(es_split):
				if i==0:
					self.DB.append_to_graph(entry, "diagnosis")
				else:
					self.DB.append_to_graph(entry, "symptom")

			self.DB.es_length = len(es_split)
			import pdb; pdb.set_trace()




		# 	self.DB.append_to_graph(self.entryWidget.get().strip())
		# 	self.DB.save_graph()
		# 	tkMessageBox.showinfo("Confirmation", "%s has been added." % self.entryWidget.get().strip())
		# 	self.entryWidget.delete(0, END)	
		# self.SetGraphStatistics()
		# self.entryWidget.focus_set()






		self.root.mainloop()



def main():
	
	mainwindow = MainWindow()

if __name__ == '__main__':
    main()