import unittest

from src.constants import DEFAULTGATEWAYCONTROLLER
from src.objects.leaf import Leaf
from src.objects.node import Node
from src.objects.tree import Tree

class TestTreeClass(unittest.TestCase):
    test_tree = Tree("test")

    def test_add_node(self):
        test_node = Node("local", "from")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        # Add the node to the tree
        self.test_tree.add_node(test_node)
        # Check if the node was added
        self.assertEqual(len(self.test_tree.nodes), 1)
        self.assertEqual(list(self.test_tree.nodes.keys()), ["from local"])


    def test_get_node(self):
        # Get the added node
        test_node = self.test_tree.get_node("from local")
        # Check if the leaves match
        self.assertEqual(test_node.get_leaves(DEFAULTGATEWAYCONTROLLER), [Leaf()])
        # Get a non-existing node
        test_none = self.test_tree.get_node("from internet")
        # Verify that it returns a None
        self.assertEqual(test_none, None)

    def test_get_all_nodes(self):
        # Check the list retuned.
        self.assertEqual(list(self.test_tree.get_all_nodes().keys()), ["from local"])
        # Add a new node to the tree
        test_node = Node("internet", "to")
        test_node.add_leaf(Leaf(), "10.10.10.10")
        self.test_tree.add_node(test_node)
        # Check the list of keys of the returned dict
        self.assertListEqual(list(self.test_tree.get_all_nodes().keys()), ["from local", "to internet"])
        self.assertDictEqual(self.test_tree.get_all_nodes(), self.test_tree.nodes)

    def test_get_num_leaves(self):
        # Get the number of leaves
        self.assertEqual(self.test_tree.get_num_leaves(), 2)
