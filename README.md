# **Node Traversing through different types of graphs**

The subject of this thesis is the implementation of algorithms for solving the problem of moving between nodes in
various types of graphs. There are different implementations, each one tries to either solve or find the best possible
movement for a bot to move between the maximum numbers of nodes possible, with the best case scenario being to move
through all of them.

## **Line Graph Implementation**

The idea here is that we have a line graph with nodes where the bot tries to reach as many nodes as possible before they
expire with the least moves possible. In order to run the simulation you need to have installed Python (the version of
I used is 3.14) the files LineGraph.py and visualize_graph.py. To run the simulation put both files in the same folder
and run in the command prompt the line 'python visualize_graph.py'. A window will pop, and you will see something like this:
![Figure_1.png](../Figure_1.png) . By pressing the button "Step" the bot(green circle) moves towards the target
(orange circle). Each node the bot goes though turns blue, meaning it reached this node before it expired.