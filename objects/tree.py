from objects.node import Node

class Tree:

    def __init__(self, device_name):
        self.device_name = device_name

        self.nodes = {}

    def add_node(self, node):
        if type(node) is Node:
            node_name = node.dir + " " + node.comp
            self.nodes[node_name] = node
        else:
            print("ERROR! Expected type: Node, received type: " + type(node))

    def get_node(self, node_name):
        return self.nodes[node_name] if node_name in self.nodes else None
    
    def get_all_nodes(self):
        return self.nodes