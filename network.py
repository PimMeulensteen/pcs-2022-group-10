import networkx as nx
from road import *

class Network:
    def __init__(self):
        self.G = nx.DiGraph()
        pass

    def add_road(self, s, e, id):
        r = Road(s, e, id)
        self.G.add_node(r)

        print(self.G.nodes[r])

        #check for edges


N = Network()
N.add_road([100,100],[200,200],0)