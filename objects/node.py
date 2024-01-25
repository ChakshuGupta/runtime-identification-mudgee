from objects.leaf import Leaf

class Node:
    
    def __init__(self, comp, dir):
        # component: internet / local
        self.comp = comp
        # direction of communication
        self.dir = dir

        self.edges = {}

    def add_leaf(self, leaf, domain):
        if type(leaf) is Leaf:
            if domain not in self.edges:
                self.edges[domain] = []
            self.edges[domain].append(leaf)
        else:
            print("ERROR! Exepected type: Leaf, received type: "+ type(leaf))
    
    def get_leaves(self, domain):
        return self.edges[domain]

    def get_edges(self):
        return self.edges
    
    def get_num_edges(self):
        return len(self.edges)