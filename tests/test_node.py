import unittest

from src.constants import DEFAULTGATEWAYCONTROLLER, DNS_CONTROLLER, NTP_CONTROLLER
from src.objects.leaf import Leaf
from src.objects.node import Node

class TestNodeClass(unittest.TestCase):

    def test_add_leaf(self):
        # Create a node
        test_node = Node("local", "from")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        # Check if the leaf was added
        self.assertEqual(len(test_node.edges[DEFAULTGATEWAYCONTROLLER]), 1)

    def test_get_leaves(self):
        # Create a node
        test_node = Node("local", "from")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        # Check if the return value is same as the added leaf
        self.assertEqual(test_node.get_leaves(DEFAULTGATEWAYCONTROLLER), [Leaf()])
        # Check if the return value is None if the domain is not found
        self.assertEqual(test_node.get_leaves(DNS_CONTROLLER), None)

    def test_get_num_leaves(self):
        # Create a node
        test_node = Node("local", "from")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        test_node.add_leaf(Leaf(), DNS_CONTROLLER)
        test_node.add_leaf(Leaf(), "10.10.10.10")
        # Check if the return value is same as the number of added leaves
        self.assertEqual(test_node.get_num_leaves(), 3)
        # Try to add to existing edges in the node
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        test_node.add_leaf(Leaf(), DNS_CONTROLLER)
        self.assertEqual(test_node.get_num_leaves(), 5)

    def test_get_edges(self):
        # Create a node
        test_node = Node("local", "to")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        test_node.add_leaf(Leaf(), DNS_CONTROLLER)
        test_node.add_leaf(Leaf(), "10.10.10.10")
        # Check if the return value is same as the added edges
        # print(list(test_node.get_edges()))
        self.assertIn(DEFAULTGATEWAYCONTROLLER, test_node.get_edges())
        self.assertIn(DNS_CONTROLLER, test_node.get_edges())
        self.assertIn("10.10.10.10", test_node.get_edges())

        self.assertEqual(list(test_node.get_edges()), [DEFAULTGATEWAYCONTROLLER, DNS_CONTROLLER, "10.10.10.10"])

    def test_get_num_edges(self):
        # Create a node
        test_node = Node("local", "to")
        # Add a leaf
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        test_node.add_leaf(Leaf(), DNS_CONTROLLER)
        test_node.add_leaf(Leaf(), NTP_CONTROLLER)
        test_node.add_leaf(Leaf(), "10.10.10.10")
        # Check if the return value is same as the number of added edges
        self.assertEqual(test_node.get_num_edges(), 4)

        # Try to add to existing edges in the node
        test_node.add_leaf(Leaf(), DEFAULTGATEWAYCONTROLLER)
        test_node.add_leaf(Leaf(), DNS_CONTROLLER)
        # The number of edges should be the same
        self.assertEqual(test_node.get_num_edges(), 4)