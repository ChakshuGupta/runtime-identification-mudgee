from node import Node

class Tree:

    def __init__(self, device_name):
        self.device_name = device_name

        self.nodes = {}

    def add_node(self, node):
        node_name = node.dir + " " + node.comp
        self.nodes[node_name] = node

    def get_node(self, node_name):
        return self.nodes[node_name]
    
    def get_all_nodes(self):
        return self.nodes