from objects.leaf import Leaf

class Node:
    
    def __init__(self, comp, dir):
        """
        The main nodes of he
        """
        # component: internet / local
        self.comp = comp
        # direction of communication
        self.dir = dir
        self.edges = {}

    def add_leaf(self, leaf, domain):
        """
        Add a leaf to the node
        """
        if type(leaf) is Leaf:
            if domain not in self.edges:
                self.edges[domain] = []
            self.edges[domain].append(leaf)
        else:
            print("ERROR! Exepected type: Leaf, received type: "+ type(leaf))
    
    def get_leaves(self, domain):
        """
        Return the leaves linked to a particular edge
        """
        if domain not in self.edges.keys():
            return None
        return self.edges[domain]

    def get_num_leaves(self):
        """
        """
        num = 0
        for domain in self.edges:
            num = num + len(self.edges[domain])
        return num

    def get_edges(self):
        """
        Return the keys of the edges linked to this node
        """
        return self.edges.keys()
    
    def get_num_edges(self):
        """
        Return the number of edges linked to this node
        """
        return len(self.edges)
    
    def print(self):
        """
        Print the node name and the associated edges
        """
        print("##### Node:" + self.dir + " " + self.comp)
        for edge in self.edges:
            print("## Edge:", edge)
            num = 0
            for leaf in self.edges[edge]:
                print("# Leaf:", num)
                leaf.print()
                num = num + 1