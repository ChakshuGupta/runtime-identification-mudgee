from edge import Edge

class Node:
    
    def __init__(self, comp, dir):
        # component: internet / local
        self.comp = comp
        # direction of communication
        self.dir = dir

        self.edges = list()

    def add_edge(self, edge):
        if type(edge) is Edge:
            self.edges.append(edge)
        else:
            print("ERROR! Exepected type: Edge, received type: "+ type(edge))
    

    def get_edge(self):
        return self.edges
    
    def get_num_edges(self):
        return len(self.edges)