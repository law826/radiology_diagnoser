import database
import unittest
from igraph import Graph
from pdb import set_trace


class TestDatabase(unittest.TestCase):

	def setUp(self):
		"""
		This will run prior to each test.
		It produces a test graph of five nodes where a-c are all interconnected.
		The nodes are named a-e.
		"""
		self.g = Graph()
		self.g.add_vertices(5)
		self.g.add_edges([(0,1), (0,2), (1,2)])
		self.g.vs["name"] = ['a','b','c','d', 'e']

	def test_AddNode(self):
		# Makes sure novel node is actually added. 
		self.g, self.node_index = database.AddNode('f', 'symptom', graph=self.g)
		self.assertEqual(self.g.vs[5]["name"], 'f')
		self.assertEqual(self.g.vs[5]["type"], 'symptom')
		self.assertEqual(self.node_index, 5)

		#And it does nothing if node name already exists.
		self.g, self_node_index = database.AddNode('a', 'symptom', graph=self.g)
		self.assertEqual(self.g.vs["name"], ['a','b','c','d','e','f'])
		self.assertEqual(self_node_index, 0)

	def test_AddAllEdges(self):
		# Add more nodes to test.
		self.g, fnode_index = database.AddNode('f', 'symptom', graph=self.g)
		self.g, gnode_index = database.AddNode('g', 'symptom', graph=self.g)
		self.g, hnode_index = database.AddNode('h', 'symptom', graph=self.g)

		# Add actual edges.
		self.g = database.AddAllEdges(self.g, [5,6,7])

		# There should now be six edges (three originally) and three just added.
		self.assertEqual(len(self.g.es), 6)
		self.assertEqual(self.g.get_eid(5,6), 3)
		self.assertEqual(self.g.get_eid(5,7), 4)
		self.assertEqual(self.g.get_eid(6,7), 5)

	def test_IdentifySimilarNodes(self):
		# Simple test that car and cart are most related and not racecars.
		self.node_tuples = database.IdentifySimilarNodes(['car', 'cart', 'racecars'])
		self.assertEqual(self.node_tuples, [('car', 'cart')])

	def test_MergeNodes(self):
		# After merging, e should remain and be connected to b and c.
		database.MergeNodes(self.g, 'e', 'a')

		self.assertEqual([node["name"] for node in self.g.vs.find(name='e').neighbors()], ['b', 'c'])
		self.assertRaises(ValueError, self.g.vs.find, name='a') 

	def test_MergeWeightedNodes(self):
		self.g.es["weight"] = 1.0
		self.g['a', 'c'] = 2
		self.g['b', 'c'] = 3

		# If a (keep) is merged with b, then it should inherit 3 edge from c.
		database.MergeWeightedNodes(self.g, 'a', 'b')
		self.assertEqual(self.g['a', 'c'], 3)
		self.assertEqual(self.g.es['weight'], [3,1.0])

		# B should have been deleted.
		self.assertRaises(ValueError, self.g.vs.find, name='b')

		self.setUp()
		self.g.es["weight"] = 1.0
		self.g['a', 'c'] = 2
		self.g['b', 'c'] = 3

		# If b (keep) is merged with a, then it should then it should keep its 3 edge with c.
		database.MergeWeightedNodes(self.g, 'b', 'a')
		#self.assertEqual(self.g['b', 'c'], 3)
		#self.assertEqual(self.g.es['weight'], None)

		self.setUp()
		self.g.es["weight"] = 1.0
		self.g['a', 'c'] = 2
		self.g['b', 'c'] = 3
		self.g['b', 'e'] = 4

		# Existent edge should be kept.
		database.MergeWeightedNodes(self.g, 'a', 'b')
		self.assertEqual(self.g['a', 'e'], 4)

	def test_IsolateSubGraph(self):
		self.g_sub = database.IsolateSubGraph(self.g, ['a', 'b', 'e'])

		# There should be three vertices and 1 edge.
		self.assertEqual(len(self.g_sub.vs), 3)
		self.assertEqual(len(self.g_sub.es), 1)
		self.assertEqual(self.g_sub.vs['name'], ['a', 'b', 'e'])

		# There should be an edge between 'a' and 'b'.
		self.assertEqual(self.g_sub.get_eid(0, 1), 0)

	def test_NodesInOrderOfCentrality(self):
		# Make a the most highly connected node.
		database.AddNode('f', 'symptom', self.g)
		database.AddNode('g', 'symptom', self.g)
		database.AddNode('h', 'symptom', self.g)
		database.AddAllEdges(self.g, [0, 3, 5, 6, 7])

		list_of_tuples = database.NodesInOrderOfCentrality(self.g, 'degree')
		self.assertEqual(list_of_tuples, [('a', 6), ('h', 4), ('g', 4), ('f', 4), ('d', 4), ('c', 2), ('b', 2), ('e', 0)])

		list_of_tuples = database.NodesInOrderOfCentrality(self.g, 'betweenness')
		self.assertEqual(list_of_tuples, [('a', 8.0), ('h', 0.0), ('g', 0.0), ('f', 0.0), ('e', 0.0), ('d', 0.0), ('c', 0.0), ('b', 0.0)])

	def tearDown(self):
		"""
		If this method is defined, the test runner will invoke this after each test. 
		"""
		pass

if __name__ == '__main__':
	unittest.main()




