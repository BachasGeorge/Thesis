# **Node Traversing through different types of graphs**

The subject of this thesis is the implementation of algorithms for solving the problem of moving between nodes in
various types of graphs. There are different implementations, each one tries to either solve or find the best possible
movement for a bot to move between the maximum numbers of nodes possible, with the best case scenario being to move
through all of them.

## **Line Graph Implementation**

The idea here is that we have a line graph with nodes where the bot tries to reach as many nodes as possible before they
expire with the least moves possible. In order to run the simulation you need to have Python installed (the version I used
is 3.14), the files LineGraph.py and visualize_graph.py. To run the simulation put both files in the same folder and
run in the command prompt the line 'python visualize_graph.py'. A window will pop, and you will see something like this:
<img width="1400" height="500" alt="Figure_1" src="https://github.com/user-attachments/assets/4fa06b51-28a8-4c0c-b3b2-5f80952cfb63" />
By pressing the button "Step" the bot(green circle) moves towards the target(orange circle). Each node the bot goes though
turns blue, meaning it reached this node before it expired. The numbers above the nodes are the weights of the edges an the
numbers below each node is their weight. After each step the weight of the nodes that have not yet been visited is reduced
by the weight of the edge the bot traversed.

The way the bot chooses where to move is in the file LineGraph.py. visualize_graph.py is generated just for the graph.

### **THIS IS AN EARLY VERSION**

The current state is really early and the way the bot moves is by always choosing the nearest end of the graph to move towards
and then sweeping the rest of the graph towards the other end. This way, if no node expires, the steps needed for the solution
are "n-1 + min(p, n-1-p)" , where n is the number of nodes and p is the index of the node the bot starts from.

In the current state the weight of the edges is picked randomly between 3 and 5 and the weight of the nodes is between 80-100.
The number of notes is 18 (so they fit in the window). What needs to get "fixed" is how we decide the weights.

!!! IMPORTANT !!!
Before the bot starts moving we check if a node expires. If a node does expire a warning is printed. This will be changed later
and a new way of picking how to traverse the path will be implimanted.

