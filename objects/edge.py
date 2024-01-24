import socket
from leaf import Leaf

class Edge:
    def __init__(self):
        self.domain = "*"
        self.leaves = list()

    def set_domain(self, ip):
        if ip != "*":
            try:
                res = socket.gethostbyaddr(ip)
                self.domain = res[0]
            except:
                self.domain = ip
        else:
            self.domain = "*"
    
    def get_domain(self):
        return self.domain
    
    def add_leaf(self, leaf):
        if type(leaf) is Leaf:
            self.leaves.append(leaf)
        else:
            print("ERROR! Argument expected of type: Leaf, but received type: "+ type(leaf))
    
    def get_leaves(self):
        return self.leaves
    
    def get_num_leaves(self):
        return len(self.leaves)
        


