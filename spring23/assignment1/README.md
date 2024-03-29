# Assignment 1: Fat Tree Mininet

In this programming assignment, you are required to create a simple fat-tree topology using Mininet.

## Fat Tree Topologies
A fat-tree topology is a type of network topology commonly used in data center networks. It is called “fat” because it has a large number of links between switches, resulting in a large amount of bandwidth available for communication.

In a fat-tree topology, switches are arranged in a hierarchical structure with multiple layers of switches. 
The lowest layer consists of access switches, which are connected to hosts. The next layer consists of aggregation switches, which are connected to multiple access switches. 
The top layer consists of core switches, which are connected to multiple aggregation switches.

This design was motivated by the steep difference in the prices between the commodity switches vs. the specialized non-commodity ones. Given the lowering cost of commodity switches, it made sense to build network topologies that only uses cheaper commodity switches, instead of using larger and more expensive non-commodity switches.

### Conventional Network topologies

![ALT TEXT](https://raw.githubusercontent.com/SNL-UCSB/cs176b-assignments/master/spring23/assignment1/oIG1u1U.png)


Around the time, when fat tree topology was proposed, data center network topologies employed a mix of commodity and non-commodity switches. The figure above illustrates a common data center topology to connect 16 hosts in those days. Here, the commodity switches are used at the edge and non-commodity ones are used at the aggregation and core levels.

### Fat tree topologies

In contrast, Fat tree only employes cheaper commodity switches at all levels. 
It considers $k$ pods, each containing two layers of $k / 2$ switches. 
Each k-port switch in the lower layer is directly connected to $k / 2$ hosts. Each of the remaining $k / 2$ ports is connected to $k / 2$ of the k ports in the aggregation layer of the hierarchy. 
There are $( k / 2 )^2$ k-port core switches.
Each core switch has one port connected to each of $k$ pods. 
The $ith$ port of any core switch is connected to pod $i$ such that consecutive ports in the aggregation layer of each pod switch are connected to core switches on $( k / 2 )$ strides. 
In general, a fat-tree built with k-port switches supports $k^3 /4$ hosts. 

To summarize, in a fat tree topology with k-port switches, we have: 
- $k$ pods 
- $k /2$ aggregation switches and access switches for each pod. Thus, across all the $k$ pods the topology has a total of $k^2 /2$ aggregation and access switches. 
- $( k / 2 )^2$ core switches 
- $k^3 /4$ end hosts 
- Total switches = $k^2 + k^2 /4=(5/4). k^2 $


The figure illustrates the fat tree topology for $k=4$, connecting 16 hosts.

![ALT TEXT](https://raw.githubusercontent.com/SNL-UCSB/cs176b-assignments/master/spring23/assignment1/F5ofoLN.png)


### Illustrative example
As an example instance of this topology, a fat-tree built from 48-port GigE switches would consist of 48 pods, each containing an edge layer and an aggregation layer with 24 switches each. The edge switches in every pod are assigned 24 hosts each. The network supports 27,648 hosts, made up of 1,152 edge (and aggregation) switches and 576 core switches. There are 576 equal-cost paths between any given pair of hosts in different pods.

## Problem
You should implement your solution in Python and use the Mininet API to create the network topology. You can use any Python libraries you find helpful for the implementation.

Your Python program (fat_tree.py) must:

- Take the number of switch ports per switch, i.e., $k$ as input(Note that $k$ cannot be negative, zero or odd number)
- It should create a fat tree topology for the input $k$ using Mininet
- Use the OVSBridge as switches. You do not need to specify any remote OF controller for this assignment.

## Additional Questions
If the cost of a 64-port 100-Gig switch is around $5,000.

- How much would it cost to create a fat-tree topology for $k=64$?
- How many hosts could it support?
- How many equal cost paths exist between hosts in different pods?
- What’s the bandwidth between any pair of hosts in this topology?


### Submission
Submit the following files over Canvas:

- Your python program, `fat_tree.py`.
- Write your answers in a text file and submit, `answers.txt`.

To copy `fat_tree.py` to your local machine for submission follow the below instructions:

First you need to copy file from VM to server.

Go to the directory where you start your VM from.
```
cd ~/cs176b-vm
```
Install the vagrant-scp plugin.
```
vagrant plugin install vagrant-scp
```
After installing it you can simply run the below command to transfer files.
```
vagrant scp default:path_to_file_on_vm destination_path_on_server
```

Now you need to copy file from server to your local machine. For that run the below command from your local machine.
```
scp snl-server-5.cs.ucsb.edu:path_to_file_on_server destination_path_on_local_machine
```


## Grading Rubric
We will assign you grades on a scale of 10.

- `Correctness`: (5 points): Does your program generate a fat-tree topology that meets the specifications given above? Here we will match the output of the dump command, generated by your program with that of ours for any arbitrary $k$.
- `Readability`: (1 points): Is your program well-documented, easy to understand, and well-organized?
- `Error Handling`: (1 point): Does your program handle any errors or invalid input gracefully?
- `Additional questions`: (3 points): Based on your answers to additional questions listed above, one point for each question. 

### Late Policy
Please submit the assignment by the advertised deadline. For late submissions, we will deduct one point (out of 10) for each day post deadline. 
