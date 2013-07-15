from __future__ import division
import os, sys, random as rand, tkMessageBox, tkFileDialog, cPickle, numpy as np, getpass, tkentrycomplete as tkcomp, re, nltk
from Tkinter import *
from pdb import *
from igraph import *

import basefunctions as bf

class DataBaseForGUI:
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