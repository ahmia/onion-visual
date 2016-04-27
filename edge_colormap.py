#!/usr/bin/env python
"""
Draw a graph with matplotlib, color edges.
You must have matplotlib>=87.7 for this to work.
"""

import matplotlib.pyplot as plt
import networkx as nx

G=nx.read_gexf("juha_nurmi.gexf")
pos=nx.spring_layout(G)
nx.draw(G,pos,node_color='#A0CBE2',edge_color='#00FFFF',width=4,edge_cmap=plt.cm.Blues,with_labels=True)
plt.savefig("edge_colormap.png") # save as png
plt.show() # display
