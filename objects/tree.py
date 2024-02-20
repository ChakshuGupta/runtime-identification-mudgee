from objects.node import Node

class Tree:

    def __init__(self, device_name, default_gateway="127.0.0.1"):
        """
        Generate the device profile tree
        """
        self.device_name = device_name
        self.default_gateway = default_gateway
        # nodes are stored as a dict with node name as the key.
        # node name is the combination of the direction of 
        self.nodes = {}

    def add_node(self, node):
        """
        Add node to the tree
        """
        if type(node) is Node:
            node_name = node.dir + " " + node.comp
            self.nodes[node_name] = node
        else:
            print("ERROR! Expected type: Node, received type: " + type(node))

    def get_node(self, node_name):
        """
        Get the leaves of a particular node
        """
        return self.nodes[node_name] if node_name in self.nodes else None
    
    def get_all_nodes(self):
        """
        Get all the nodes of the tree
        """
        return self.nodes
    
    def get_num_leaves(self):
        """
        Computes the total number of leaves in the tree and returns the number.
        """
        num = 0
        for node in self.nodes:
            num = num + self.nodes[node].get_num_leaves()
        return num
    
    def print(self):
        """
        Print the profile tree
        """
        print("***************************************************")
        print("###########  " + self.device_name)
        for node in self.nodes:
            self.nodes[node].print()
        print("***************************************************\n")

    def is_empty(self):
        """
        Return if the tree has any nodes or not.
        """
        if len(self.nodes.keys()) == 0:
            return True
        return False