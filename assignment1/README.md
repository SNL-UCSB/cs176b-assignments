# CS 176B: Assignment 1

## Learning Objectives
In this assignment, you will learn:
1. How to create Mininet topologies for prototyping network monitoring solutions?
2. How to write packet-processing pipelines for network monitoring in P4?
3. How to analyze queue sizes and bottlenecks within a Mininet network?

This assignment builds up on topics covered in CS 176B lectures and discussion section. More specifically, it focuses on how we can use SDN tools to design experiments for network research. We will focus on network telemetry systems, which are designed to query the state of the network. In this assignment, we will specifically focus on the design of a network telemetry system that monitors the queue sizes for different switches in the network. The first part of assignment will focus on the building blocks for the network telemetry system, i.e. Mininet-based topology and the P4-based packet processing pipeline. The second part will focus on using this telemetry system to measure the state of the network under different network conditions. 

# Topology

<!-- ![](https://i.imgur.com/aEjal7h.jpg)
![Topology](https://i.imgur.com/LDnggyt.png) 
![](https://i.imgur.com/h3w07t1.jpg)
![](https://i.imgur.com/IcetmqC.png)
-->

![Topology](https://i.imgur.com/Qs0ghZZ.png)

We will use the topology shown above for this assignment. This topology has four programmable switches (S1-4). We can program the packet-processing pipeline for these switches using the P4 language. For this assignment, we will program the switch to forward packets and perform in-band network telemetry. We have three links, S3-S1, S1-S2, and S2-S4. We have four hosts, where the host H1-2 are connected to switch S3, and H3-H4 are conncted to switch S4. All the four switches are connected to a monitor host. 

<!-- ##### Switches: 


##### Links: 
Each link in this topology is configurable by defining relevant parameters (bandwidth, packet loss, etc.) in Mininet. Bottleneck links will have an impact on where the packets are queued up.

##### Hosts:
Host 1,2,3,4 are virtual hosts that send and receive packets from each other in the network.

##### Monitor:
The monitor host only receives and processes the headers of each packet. If any of the switches is in an undesirable state, it can raise a warning. The monitor will not respond to pings from other hosts as it is just a sink to receive duplicated probe packets from each switch. -->


# Part 1: Building Blocks
For this assignment, we will use Mininet to emulate the topology shown above, and use P4 language to configure the packet processing pipelines for the software switches. 

## Task 0: Setup the VM
In assignment 0, you used `vagrant` to setup the VM. For this assignment, we need to install a few missing dependencies on our VM.
1. Run a ```git pull``` in the directory to get any new commits
2. Enter the ```assignment0``` directory containing the Vagrantfile for your VM.
3. Turn on the VM ```vagrant up```
4. Log into the VM ```vagrant ssh```
5. After logging in, clone this repo (cs176b-assignments) onto your VM and cd into the ```assignment1``` directory.
6. Run the provided setup script (```./setup.sh```) on your VM and wait for the installation to finish.

## Task 1: Create Network Topology.
The goal of this task is to write the Python script that uses Mininet to emulate the topology shown above. For your convenience, we have provided a template file, [`start_mininet.py`](#) that you can edit. 

You can run this file using the `Makefile` provided for you. This file takes care of compiling your P4 program and running `start_mininet.py`. The `Makefile` prints out and executes the commands needed to be run, to compile your P4 program and start Mininet. You can use these commands to compile your P4 program separately or start Mininet without recompiling your P4 program.

The file that we provided is not complete. Thus, when you try running the command `pingall`, it won't work. Your task is to add the necessary links to realize the topology shown above. We've set the default link type in Mininet as `TCLink`, this allows us to modify characteristics of the link such as bandwidth, delay, loss, and queue size. For your reference, we have provided `TODO` comments for you in the `init()` function of the `CoreP4Topo` class. Make sure to add the links in the specified order for traffic to be routed correctly. 

To check if you have added all the missing links correctly, you can run the `pingall` command. On successful completion, you should expect to see that all the hosts are able to ping each other. The monitor will not respond correctly to pings from the other hosts, since it is just a sink to receive packets. You will see an `X` for each host when it tries to ping the monitor. After waiting for the full duration of the `pingall` test you should see the following output: 
```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 X 
h2 -> h1 h3 h4 X 
h3 -> h1 h2 h4 X 
h4 -> h1 h2 h3 X 
monitor -> X X X X 
*** Results: 40% dropped (12/20 received)
```

***

## Task 2: Configure pcket-processing pipelines
The goal of this task is to use the P4 language to configure the packet processing pipelines for the four switches (S1-S4). In addition to packet forwarding, these switches perform in-network telemetry. More concretely, they detect probe packets with a custom IP header, and add the state of the switch, i.e., `swid` and `queue_size` to a duplicated packet that is forwarded to the network monitor. 




The packet processing pipelines at these switches perform the following tasks. In the ingress portion of the pipeline we will clone any packet received to go through the egress pipelines and send to the monitor. In the egress processing, we check if the packet is a cloned packet, and if so, we forward the packet to the monitor with the switch/queue size information added to the IP header ONLY if the following conditions are met, otherwise we drop the cloned packet:
* Condition 1: The packet is a probe packet containing a valid Switch Inspector (SI) header
* Condition 2: The queue size of the switch is greater than the `queue_threshold` constant



For your convenience, we have provided the template file, `monitor.p4`. Please fill in the TODO comments in the ingress and egress processing part of the pipelines. Please refer to Case 0 in the experiment section below to test your P4 implementation.

**Note**
This task has some similarities with the [Multi-hop route inspector (MRI)](https://github.com/p4lang/tutorials/tree/master/exercises/mri) tutorial. However, unlike MRI, it clones the probe packets, adds the queue size information for just one switch, and compares the queue size value with a threshold value before sending it to the monitor. 

### Bonus Tasks
We encourage the interested students to further optimize the packet processing pipeline for bonus points.
* The current pipeline clones all the packets from ingress to egress. Optimize this pipeline, such that it selectively clones the probe packets for which the queue size exceeds the threshold. (20 points)
* The current pipeline uses a hardcoded value as threshold. Changing this value requires recompiling the P4 program, which is expensive. Optimize this pipeline, such that it can dynamically update the threshold value. One possible approach can be to use a match-action table, where the action can be to read the threshold value from memory, and write it to packet's metadata. (40 points)
* The current pipeline can only add the queue size information to specialized probe packets. Thus, the queue size information can only be actively probed from the network. Enabling passive monitoring of queue sizes is more desirable, where for every incoming packet, it reads the queue size and report the ones that exceed the threshold to the monitor. Thus, one bonus task will be to enable passive monitoring for these switches. (40 points)

***

## Task 3
### Use Python to write data processing and analysis scripts
In this task you will write Python code for the monitor to receive and process the SI headers that are reporting the queue size at each switch.
Implement the `handle_pkt` function in `monitor_receive.py` which will handle packets being received on each of the monitor's interfaces. Currently, the function just prints out the contents of each packet received. We want to extract the switch ID and queue size from each packet. We can then write these values to a CSV file with the following format:
```time, switch_id, queue_size```
Then implement `graph_queues.py` which reads in this CSV file and plots the queue size over time for each switch. Please label the axes appropriately and add a title to your graph.

***

***

# Part 2: Measuring Network's State
<!--Overview.

For each case, clarify
- What's the goal of the experiment?
- What specific changes in network configuration are required to run the experiment?
- What specific metrics they need to collect/plot/analyze?
-->
The goal of the experiments is to observe how different bottleneck links affect where and when the queue size is building up with the presence of backgroud iperf traffic. 

## Task 0: Testing out P4 Program
For these experiments we will be generating tcp traffic using iperf between h1 and h4. We will change the capacity of certain links and observe how the behavior changes. First, we will test out sending traffic between the hosts with unconstrained links. Set the queue threshold in monitor.p4 to 0 for now, since the links are not constrained. Uncomment the call to `experiment()` in `start_mininet.py`. You should be able to view the output from each host in the `logs` directory. On h4 we will run `./start_server.py` and on h1 we will run `./start_client.py`. We will be running background iperf traffic between hosts h2 and h3. The monitor and h4 will be running `monitor_receive.py` and `receive.py` respectively, which will listen and log packets that arrive at that host. Remember, you can open terminal windows for each host using `xterm h1 h2 ...` for debugging purposes, however, this may become tedious over time. We can programatically run commands on each host using the `cmd()` command as we have done in the `experiment()` function. Make sure to properly indicate the path of the scripts that are being executed. If your P4 program is working correctly, you should be able to see packets in the monitor's log displaying the switch ID and queue size over time. Once you have verified your P4 implementation is correctly adding SI headers, change `queue_threshold` back to a value of 10.

## Task 1: Reduced capacity for S1-S3
Set the bandwidth of the S1-S3 link to 200 Kbps.
For this experiment, we first alter the link `s1-s3` to a bandwidth 200 Kbps. The goal of this experiment is to investigate where and when the queue size at any switch exceeds the `queue_threshold`. After logging the data with `monitor_receive.py`, use `graph_queues.py` to graph the queue size of each switch over time. Repeat the same analysis for Case 2 & 3.
<!--
(Just some possible ideas)
- Number of times packets were sent to monitor from each switch (i.e. number of times a warning is raised for each switch)
- The queue length of each switch in a time series 
- The average time packets have to wait in the queue for each switch
- The variance of waiting time
- Ratio of waiting time before and after changes VS ratio of changes in bandwidth
-->

## Task 2: Reduced capactiy for S1-S2 and S1-S3
Set the bandwidth of the S1-S2 link to 100 Kbps.
Set the bandwidth of the S1-S3 link to 200 Kbps.


## Task 3: Reduced cpacity for S1-S2, S1-S3, and S2-S4
Set the bandwidth of the S1-S2 link to 100 Kbps.
Set the bandwidth of the S1-S3 link to 200 Kbps.
Set the bandwidth of the S2-S4 link to 200 Kbps.

# Deliverables
The following are the deliverables for this assignment:
* `start_mininet.py`
* `monitor.p4`
* `monitor_receive.py`
* 3 graphs for Case 1, 2, 3

Please send these deliverables to the teaching staff, Sanjay, over email. Please cc Arpit and Jiamo to that email.  

In case you tried to solve the bonus point problems, then please send us a small writeup explaining how you implemented and tested the new features. 



