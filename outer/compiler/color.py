


class GraphNode:
    def __init__(self,d,e = []):
        self.data = d
        self.edges = set(e)
    def __iter__(self):
        for e in self.edges:
            yield e
    def add_edge(self,other):
        if other not in self.edges:
            self.edges.add(other)
            other.add_edge(self)
    def remove_edge(self,other):
        if other in self.edges:
            self.edges.remove(other)
            other.remove_edge(self)
    def __repr__(self):
        return "Node("+repr(self.data)+")"



def random_graph(size,connections = 20):
    nodes = [GraphNode(i) for i in range(size)]
    graph = Graph(nodes)
    top = size*(size-1)//2
    import random
    import math
    def untri(t):
        x = int(((t+1)*2)**.5+.5)
        y = int(t-math.floor((math.sqrt(1+8*t)-1)/2)*math.floor((math.sqrt(1+8*t)+1)/2)/2)
        return x,y
    for e in random.sample(range(top),connections):
        x,y = untri(e)
        nodes[x].add_edge(nodes[y])
    return graph
    

    
def next_color(s):
    i = 0
    while 1:
        if i not in s:
            return i
        i += 1
class ColoredNode(GraphNode):
    def __init__(self,d,c=0,e=[]):
        super().__init__(d,e)
        self.edge_colors = set((ed.color for ed in e))
        self.color = c if c is not None else next_color(self.edge_colors)
    def set_edges(self,e):
        self.edge_colors = set((ed.color for ed in e))
        self.color = next_color(self.edge_colors)
        for ed in e:
            self.add_edge(ed)
    def add_edge(self,other):
        if other not in self.edges:
            self.edge_colors.add(other.color)
            super().add_edge(other)
    def remove_edge(self,other):
        if other in self.edges:
            self.edge_colors.remove(other.color)
            super().remove_edge(other)
    def __repr__(self):
        return "ColoredNode{"+repr(self.color)+"}("+repr(self.data)+")"
    
                  
class Graph:
    def __init__(self,n=[]):
        self.nodes = set(n)
    def add(self,node):
        self.nodes.add(node)
    def remove(self,node):
        self.nodes.remove(node)
    def __iter__(self):
        for n in self.nodes:
            yield n
    
def color(grph,autosort=True):#sort with key=lambda x: -len(x.edges) for better performance
    colored = Graph()
    newnodes = dict()
    for node in (sorted(grph,key=lambda x: -len(x.edges)) if autosort else grph):
        g = ColoredNode(node)
        colored.add(g)
        newnodes[node] = g
        g.set_edges(set((newnodes[e] for e in node.edges if e in newnodes)))
    return colored

def perfect_color(grph):
    colored = Graph()
    newnodes = dict()
    for node in grph:
        g = ColoredNode(node)
        colored.add(g)
        newnodes[node] = g
        g.set_edges(set((newnodes[e] for e in node.edges if e in newnodes)))
    top = score(colored)
    nodes = list(colored.nodes)
    def try_color(c,i,clrs,nodes,pr=0):
        if pr:
            print('coloring',nodes[i].data,'with color',c,'/',clrs)
        nodes[i].color = c
        for n in nodes[i].edges:
            if n.color == c:
                nodes[i].color = -1
                if pr:
                    print('failed against',n.data)
                return False
        if i+1 == len(nodes):
            return True
        for cl in range(clrs):
            if try_color(cl,i+1,clrs,nodes,pr):
                return True
        nodes[i].color = -1
        return False
    for i in range(top):
        for n in nodes:
            n.color = -1
        print(i+1,'/',top,end="  \r")
        if try_color(0,0,i+1,nodes):
            return colored
    return color(grph)
    try_color(0,0,i+1,nodes,1)
    print("failed to color")
    print({n.data:[e.data for e in n.edges] for n in grph})
    print("other's proposed coloring")
    print({n.data.data:n.color for n in color(grph)})
    assert False
    
            

def score(graph):
    maxcolor = -1
    for n in graph:
        maxcolor = max(maxcolor,n.color)
    return maxcolor
