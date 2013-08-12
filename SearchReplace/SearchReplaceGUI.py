from __future__ import division
import os, sys
sys.path.append(os.path.realpath('..'))
import tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *

sys.path.append(os.path.realpath('..'))
import basefunctions as bf
import nltk
from importnlp import ImportNLP


"""
Perform search and replace.
"""


class SaveData:
	def __init__(self):
		self.replacement_tuples = []
		self.user_settings = dict()
		pass

	def Save(self):
		cPickle.dump(self, open('SearchReplace/search_replace_save_data.p', 'wb'))

class SearchReplaceGUI:
	def __init__(self):
		self.LoadUserSettings()

	def main(self):
		self.root = Tk()
		self.root.title('Search and Replace Terms')

		

		gui_elements = [self.EntryUI,
						self.CurrentFileUI,
						self.ListboxUI,
						self.ButtonsUI
		]

		self.gui_element_dict = {}

		for startingrow, gui_element in enumerate(gui_elements):
			self.gui_element_dict[gui_element] = startingrow
			gui_element(startingrow=startingrow)

		# Feature for applying old mappings.

		self.root.mainloop()

	def LoadUserSettings(self):
		try: 
			self.sd = cPickle.load(open('SearchReplace/search_replace_save_data.p', 'rb')) # Pickle with dict of current directory mapped with save directories.
			if os.getcwd() in self.sd.user_settings:
				self.doc_path = self.sd.user_settings[os.getcwd()]
			else:
				tkMessageBox.showinfo("Please choose a file to modify.")	
				self.SetFile()
		except (IOError, cPickle.UnpicklingError):
			self.sd = SaveData()
			tkMessageBox.showinfo("New User/Computer Detected", "Please choose a file to modify.")
			self.SetFile()

	def SetFile(self):
		self.doc_path = tkFileDialog.askopenfilename(title = 'Please choose a save directory')
		self.sd.user_settings[os.getcwd()] = self.doc_path
		self.sd.Save()

###########
	def EntryUI(self, startingrow=0):
		self.euf = Frame(self.root)
		self.euf.grid(row=startingrow, columnspan=2)

		self.entrylabel = bf.Label(self.euf, text="Please enter two terms separated by commas. The first will be kept.")
		self.entry = bf.Entry(self.euf, self.EntrySubmitted)

	def EntrySubmitted(self, event=0):
		es_split = bf.ParseEntryCommaSeparated(self.entry, "Error")
		self.sd.replacement_tuples.append(tuple(es_split)) # Add to tuples list.
		self.sd.Save() # Save to pickle.
		self.ListboxUI(startingrow = self.gui_element_dict[self.ListboxUI], updatemode=True) # Update listbox.
		self.entry.delete(0,END) # Clear entry box.


###########
	def CurrentFileUI(self, startingrow=0):
		self.CFU_frame = Frame(self.root)
		self.CFU_label = Label(self.CFU_frame, text="File to modify: %s" %self.doc_path)
		self.CFU_label.pack()
		self.CFU_frame.grid(row = startingrow, columnspan = 2)

	def CurrentFileUIUpdate(self):
		try:
			self.CFU_label.pack_forget()
		except AttributeError:
			pass
		self.CFU_label = Label(self.CFU_frame, text=self.doc_path).pack()

###########
	def ListboxUI(self, startingrow=0, updatemode=False):
		if updatemode == False:
			self.lbf = Frame(self.root)
			self.lbf.grid(row=startingrow, columnspan = 2)
			self.listbox = Listbox(self.lbf, width=80)
		elif updatemode == True:
			self.listbox.delete(0, END)
			self.listbox.pack_forget()


		try: 
			for pair in self.sd.replacement_tuples:
				self.listbox.insert(END, "Keep '%s' Replace '%s'" %(pair[0], pair[1]))
		except AttributeError:
		# If there are no items yet.
			pass

		self.listbox.pack()

###########
	def ButtonsUI(self, startingrow=0):
		self.buttons_frame = Frame(self.root)
		button_labels = ["Update File",
						"Extend Brackets",
						"Debug Mode",
						"SetFile",
						"Delete Item",
						"Open File"
			]

		button_commands = [self.UpdateFileButtonPressed,
							self.ExtendBracketsButtonPressed,
							self.DebugModeButtonPressed,
							self.SetFileButtonPressed,
							self.DeleteItemButtonPressed,
							self.OpenFileButtonPressed
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.buttons_frame, text=label, default="normal", command=button_commands[button_number]).pack(side = LEFT)

		self.buttons_frame.grid(row=startingrow, columnspan = 2)

	def UpdateFileButtonPressed(self):
		self.inlp = ImportNLP(self.doc_path)
		self.full_count = 0
		for pair in self.sd.replacement_tuples:
			self.inlp.SearchReplace(pair[0], pair[1])
			self.full_count += self.inlp.number_replaced

		result = tkMessageBox.askquestion("Replace", "Are you sure you want to replace %s items?" %self.full_count, icon='warning')
		if result == 'yes':
			text_file = open(self.doc_path, 'w')
			text_file.write(self.inlp.raw)
			text_file.close()
		else:
			pass

	def ExtendBracketsButtonPressed(self):
		self.inlp = ImportNLP(self.doc_path)
		self.inlp.ExtendBracketsInFile()

	def DebugModeButtonPressed(self):
		import pdb; pdb.set_trace()

	def SetFileButtonPressed(self):
		self.SetFile()
		self.CurrentFileUIUpdate()

	def DeleteItemButtonPressed(self):
		selected_index = int(self.listbox.curselection()[0])
		del self.sd.replacement_tuples[selected_index]
		self.ListboxUI(startingrow = self.gui_element_dict[self.ListboxUI], updatemode=True)
		self.sd.Save()

	def OpenFileButtonPressed(self):
		os.system("open " + self.doc_path)

###########

if __name__ == '__main__':
		srg = SearchReplaceGUI()