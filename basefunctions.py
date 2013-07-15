from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
import Tkinter as tk
from pdb import *
from igraph import *


def Label(parent, text):
	"""
	Tkinter label that simply packs into a frame. 
	"""
	label = tk.Label(parent)
	label["text"] = text
	label.pack()

def Entry(parent, action, completion_list=None, width = 50, binding = "<Return>", focus=True):
	"""
	Tkinter entry that simply packs into a frame and autocompletes from a list.
	"""
	entry = tkcomp.AutocompleteEntry(parent)
	entry.set_completion_list(completion_list)
	entry["width"] = width
	entry.pack()
	entry.bind(binding, action)
	if focus:
		entry.focus_set()

	return entry

def ParseEntryCommaSeparated(entryWidget, emptyErrorMessage):
	"""
	Takes an entry widget input and parses so that an array of items without spaces are commas are returned.

	"""
	if entryWidget.get().strip() == "":
		tkMessageBox.showerror("Tkinter Entry Widget", emptyErrorMessage)
		es_split = []
	else:
		entrystring = entryWidget.get().strip()
		es_split_pre = entrystring.split(",")
		es_split = [x.lstrip() for x in es_split_pre]

	return es_split

