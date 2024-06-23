import networkx as nx

class Graph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node):
        self.graph.add_node(node)

    def add_edge(self, source, dest, transport_type):
        self.graph.add_edge(source, dest, transport_type=transport_type)
