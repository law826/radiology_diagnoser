#!/usr/bin/env python
# encoding: utf-8
"""
radiology_diagnoser.py

Started by LN on 7/4/13
"""
import os
import sys
import random as rand
from Tkinter import *
import tkMessageBox
import tkFileDialog 
import cPickle
import numpy as np
import igraph
import getpass
from pdb import *


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

				
	def save_graph(self):
		try:
			self.g.write_pickle(os.sep.join([self.save_path, "graph.p"]))
		except:
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a valid save path (current path is %s)" %self.save_path)

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

		self.LabelEntryUI()
		self.ButtonUI()

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
		DiagnosisCharterizationWindow()

	def SetPath(self):
		self.DB.save_path = tkFileDialog.askdirectory(title = 'Please choose a save directory')\

class DiagnosisCharterizationWindow:
	def __init__(self):
		self.MakeUI()

	def MakeUI(self):
		self.root = Tk()
		self.root.title("Diagnosis")


		self.LabelEntryUI()

		self.root.mainloop()




	def LabelEntryUI(self):
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)		
				
		# Create a Label in textFrame
		self.entryLabel = Label(self.textFrame)
		self.entryLabel["text"] = "Enter the diagnosis:"
		self.entryLabel.pack(side=LEFT)
	
		# Create an Entry Widget in textFrame
		self.entryWidget = Entry(self.textFrame)
		self.entryWidget["width"] = 50
		self.entryWidget.pack(side=LEFT)
		self.entryWidget.focus_set()
		self.entryWidget.bind("<Return>", self.AddButtonPressed)
		self.textFrame.pack()







		self.root.mainloop()



def main():
	
	mainwindow = MainWindow()

if __name__ == '__main__':
    main()