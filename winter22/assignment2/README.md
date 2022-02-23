# CS 176B: Assignment 2

In the previous assignment, you learned how we can use probe packets to measure queue sizes in the network. In this assignment, we will learn how to enable passive monitoring of queue sizes and how to handle network congestion at runtime.

## Learning Objectives
In this assignment, you will learn:
1. How to express the pipeline for packet-cloning in P4?
2. How to use p4runtime to update the network's routing policy at runtime?

## Topology
<!--![Topology](https://i.imgur.com/Qs0ghZZ.png)-->
![](https://i.imgur.com/tqlMSaL.png)


The topology for this assignment is similar to the one in Assignment 1 except, there is an additional link between `s1` and `s4`. The link `s1-s2` is bottlenecked and supports a maximum packet rate of `80` packets per second (pps), which translates to a data rate of ~1Mbps for ~1500 bytes packets (near-MTU size).

## Traffic
There is a constant bandwidth (~500 Kbps) UDP traffic from `h2` to `h3` and from `h1` to `h4`. The traffic `h2-->h3` starts at `t=0` and ends at `t=20`. The traffic `h1-->h4` starts at `t=5` and ends at `t=15`.

## Initial routing policy
All the traffic between `h1-->h4` and `h2-->h3` takes the route `s3-->s1-->s2-->s4`. In other words, the routing policy does not use the link `s1-s4`. Note that this initial routing policy is specified in the `sX-runtime-init.json` files.

## What is Passive Monitoring?
Passive monitoring is a technique used to capture traffic and other statistics from network in a non-disruptive fashion. In contrast to active monitoring, it does not actively sends a measurement probe, and monitors the network passively.

In this assignment, we create a passive-monitor named `monitor` which observes the queue buildups at various links in the network. We also learn how to program the switches to report queue buildup information to the monitor.

## What is P4Runtime? What are runtime commands?
A P4 program by itself only describes a partial behavior of a switch. Consider the following match-action table taken from [switch.p4][sp4]:
```p4
table ipv4_lpm {
    key = {
        hdr.ipv4.dstAddr: lpm;
    }
    actions = {
        ipv4_forward;
        drop;
        NoAction;
    }
    size = 1024;
    default_action = NoAction();
}
```
The table above describes the match key, the possible actions it can take and the default action. However, it fails to describe which action is executed upon what match. Such information is usually provided by a *Runtime API*. More concretely, the P4 program is static and defines a general template for the switch. However, a Runtime API allows usage of *runtime commands* to specify/modify the behavior of the switch at runtime. In the current assignment, we use `sX-runtime-init.json` file to describe the bootstrapping runtime commands for the switch `sX`.

Shown below is a table entry pulled out from [s1-runtime-init.json][s1rj] file:
```json
{
  "table": "MyIngress.ipv4_lpm",
  "match": {
    "hdr.ipv4.dstAddr": ["10.0.3.0", 24]
  },
  "action_name": "MyIngress.ipv4_forward",
  "action_params": {
    "dstAddr": "08:00:00:00:03:00",
    "port": 2
  }
}
```
The above table entry states, *if a `ipv4.dstAddr` matches the IP `10.0.3.0/24`, forward the packet through the port 2 of the switch.*

P4Runtime is a runtime API which is used for adding/deleting/modifying table entries and other runtime objects (e.g., clone entries, multicast entries, etc.).

## Directory Structure
For your convenience, we have provided an overview of the directory structure for this assignment. Below, you can find description for different files in this directory.
```
.
├── graph_queues.py      # Plotting script
├── monitor-receive.py   # The monitoring script running on the node "monitor"
├── p4runtime_lib        # P4 runtime library for sending runtime cmds to the switches
│   ├── ...
├── p4runtime_switch.py
├── s1-runtime-init.json # The bootstrapping switch configuration file for s1
├── s2-runtime-init.json # The bootstrapping switch configuration file for s2
├── s3-runtime-init.json # The bootstrapping switch configuration file for s3
├── s4-runtime-init.json # The bootstrapping switch configuration file for s4
├── send.py              # The script used to send UDP traffic between hosts at a constant bandwidth
├── start_mininet.py     # Creates the mininet topology
├── switch_entries.py    # Contains a convenience function to re-configure the switches at runtime
├── switch.p4            # The p4 file used to program the switches
└── ...                  # Other convenience scripts
```

-----
-----
## Tasks
### Task 0: Setup VM
Follow the steps below to setup the VM for Assignment 2:
* Run `git pull origin master` in the assignments directory to pull latest changes.
* Install tcpreplay on your VM by running:
```cmd
sudo apt install tcpreplay
```

Go to the root directory of the Assignment 2 and run `make`. Your mininet topology for the Assignment 2 is up and working! You can verify this by running `pingall 1` in the mininet CLI (`1` second is the timeout). You should expect the following output:
```
mininet> pingall 1
*** Ping: testing ping reachability
h1 -> h2 h3 h4 X
h2 -> h1 h3 h4 X
h3 -> h1 h2 h4 X
h4 -> h1 h2 h3 X
monitor -> X X X X
*** Results: 40% dropped (12/20 received)
```
Note that similar to the Assignment 1, the monitor will not respond to the pings as it is just a collector.

Run `make clean` for cleanup.

#### Mininet commands
You can verify the network topology described above in the [Topology Section](#Topology) by running the `net` command as shown below:
```
mininet> net
h1 eth0:s3-eth2 h1-eth1:eth0
h2 eth0:s3-eth3
h3 eth0:s4-eth2
h4 eth0:s4-eth3
monitor eth0:h1-eth1 monitor-eth1:s1-eth3 monitor-eth2:s2-eth3 monitor-eth3:s3-eth4 monitor-eth4:s4-eth4
s1 lo:  s1-eth1:s2-eth1 s1-eth2:s3-eth1 s1-eth3:monitor-eth1 s1-eth4:s4-eth5
s2 lo:  s2-eth1:s1-eth1 s2-eth2:s4-eth1 s2-eth3:monitor-eth2
s3 lo:  s3-eth1:s1-eth2 s3-eth2:eth0 s3-eth3:eth0 s3-eth4:monitor-eth3
s4 lo:  s4-eth1:s2-eth2 s4-eth2:eth0 s4-eth3:eth0 s4-eth4:monitor-eth4 s4-eth5:s1-eth4
```
The command above shows all the hosts (e.g., `h1`, `h2`, etc.) and the switches (e.g., `s1`, `s2`, etc.) in the network. Further, the command also displays how the hosts and the switches are connected with each other via links. E.g., `s1` is connected to `s2` with the link `s1-eth1:s2-eth1`. `s1-eth1` is an interface/port on `s1` whereas `s2-eth1` is an interface/port on `s2`.

Another useful command is `ports` shown below
```
mininet> ports
s1 lo:0 s1-eth1:1 s1-eth2:2 s1-eth3:3 s1-eth4:4
s2 lo:0 s2-eth1:1 s2-eth2:2 s2-eth3:3
s3 lo:0 s3-eth1:1 s3-eth2:2 s3-eth3:3 s3-eth4:4
s4 lo:0 s4-eth1:1 s4-eth2:2 s4-eth3:3 s4-eth4:4 s4-eth5:5
```
The ports command (output shown below) describes which switch port uses what interface. E.g., switch `s1`'s port 1 uses the interface `s1-eth1`.

Yet another relevant command for this assignemnt is called `dump`
```
mininet> dump
<P4Host h1: eth0:10.0.3.1,h1-eth1:None pid=5932>
<P4Host h2: eth0:10.0.3.2 pid=5935>
<P4Host h3: eth0:10.0.4.3 pid=5938>
<P4Host h4: eth0:10.0.4.4 pid=5941>
<P4Host monitor: eth0:10.0.0.5,monitor-eth1:None,monitor-eth2:None,monitor-eth3:None,monitor-eth4:None pid=5944>
<ConfiguredP4RuntimeSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None,s1-eth4:None pid=5946>
<ConfiguredP4RuntimeSwitch s2: lo:127.0.0.1,s2-eth1:None,s2-eth2:None,s2-eth3:None pid=5950>
<ConfiguredP4RuntimeSwitch s3: lo:127.0.0.1,s3-eth1:None,s3-eth2:None,s3-eth3:None,s3-eth4:None pid=5959>
<ConfiguredP4RuntimeSwitch s4: lo:127.0.0.1,s4-eth1:None,s4-eth2:None,s4-eth3:None,s4-eth4:None,s4-eth5:None pid=5963>
```
The `dump` command displays the IP addresses of different interfaces in different hosts. E.g., we can see that `h1`'s `eth0` interface has the IP `10.0.3.1`. Similarly, the IP address for host `h2` is `10.0.3.2`.

-----
### Task 1: Observing queue buildup with passive monitoring
For the first task, you will modify the current setup to support passive monitoring.

#### Task 1a: Modifying switch.p4
We provide a template [switch.p4][sp4] program containing the basic forwarding functionality. In this task, you will augment [switch.p4][sp4] to add passive-monitoring capabilities. Specifically, the switch should create a clone of the current packet if the queue-size metadata on the packet is above a certain threshold.

However, unlike the previous assignment, your job is to write a more efficient cloning pipeline. More concretely, in this assignment, you will create a clone of the packet in the egress pipeline only if the queue size metadata on the packet is above a certain threshold. Recall that the Assignment 1 code cloned all the incoming packets and selectively dropped them in the egress pipeline.

In this assignment, you selectively clone packets because, when there is an over-subscriptiion for an egress port, the packets are buffered in an egress-port specific queue. Therefore, creating too many clones may result in packet-drops of the (cloned) monitoring packets.

The [switch.p4][sp4] program defines a custom header named `out_header`. It contains two fields: `swid` -- the switch id, and `qdepth` -- the depth of the queue as observed by the packet. In this task, you will add `out_header` to all the cloned packet. Then, an existing runtime rule present in the `sX-runtime-init.json` files will forward the cloned packets to the monitor.


For this task, use the following guidelines to update the P4 code in [switch.p4][sp4]:
* Complete the action `update_clone_metadata` such that the user-defined metadata field `meta.original_qdepth` contains the queue depth of the original packet.
* The action `do_clone_e2e` is incomplete. This action must make a clone of the packet such that:
    * The clone session ID of the clone is 432 and,
    * The field `meta.original_qdepth` is preserved in the cloned packet.
* In the egress pipeline,
    * If the current packet is the original packet and the queue depth is above the threshold `q_th`, clone the packet and update the metadata field `meta.original_qdepth`.
    * If the current packet is the cloned packet, add an `out_header` on it.
      * HINT: Try to see how the code in assignment 1 selectively added the SI header only to the cloned packets. Because, we are creating an E2E clone, please use the `2` as the value for the instance type. 
* Finally, please follow the other TODO comments which instruct you to uncomment some lines or remove others.

Congratulations! Now, your switch is ready to perform passive-monitoring. You can test out your newly written code by uncommenting the `experiment` function call on line 188 in [start_mininet.py][sm]. The `experiment` function runs a monitoring script on the node `monitor`, and sends the traffic as mentioned in the [Traffic](#Traffic) section. Now, when you run `make`, you should see the following files in the `logs/` directory:
* `monitor-output.txt` -- This log file contains output from the [monitor-receive.py][mr] script running on the `monitor` node.
* `switch_stats.csv` -- This csv file consists of the columns `time` -- the time at which the monitor receives the cloned packet, `swid` -- the switch experiencing congestion, and `qdepth` -- the queue depth at the switch. You will need this csv file in the [Task 1b](#Task-1b).

**Note** - Please wait for 30 seconds for the experiment to finish.

#### Task 1b
In this task you will modify the [graph_queues.py][gq] script to parse the `switch_stats.csv` file. You must store the values in the three lists defined in the python script. By running the plotting script, you should get a visual confirmation of the congestion in the network.

Shown below is a sample graph for this task. Note that the actual graph may differ sligthly from the sample graph.
![sample graph][sg]

-----
### Task 2: Changing forwarding rules at runtime
The goal of the second task is to overcome the congestion detected in Task 1. In this task, you will write a script that modifies the forwarding rules with runtime commands when congestion is detected. More precisely, to alleviate congestion, the new forwarding rules should send
* the traffic `h2-->h3` along the route `s3-->s1-->s4`
* the traffic `h3-->h2` along the route `s4-->s1-->s3`

We have provided you with some starter code in the [monitor-receive.py][mr] script. This script runs on the `monitor` node in the network. It observes all the monitoring packets and creates the `switch_stats.csv` file used in the Task 1. The logic for creating the csv file is present in the function `handle_pkt_1`. The function `handle_pkt_1` is called on each packet that is sniffed by the monitor.

The [monitor-receive.py][mr] script contains an unused function `handle_pkt_2`. As soon as this function receives the first monitoring packet indicating congestion, it calls `trigger_reprogram` function to reconfigure the switch. Unfortunately, the function `trigger_reprogram` is not complete and therefore, is not able to fix the congestion.

Please follow the guidelines below to complete this task:
* Modify the [monitor-receive.py][mr] script such that instead of `handle_pkt_1`, the function `handle_pkt_2` is called on each sniffed packet.
* `trigger_reprogram` function copies the `sX-runtime-init.json` files and creates `sX-runtime.json` files. Your task is to modify the `sX-runtime.json` files programmatically to enforce the new routing policy.

**TIP:** Recall that we covered the forwarding table entry structure in the section about [P4Runtime](#What-is-P4Runtime-What-are-runtime-commands). Also recall the useful mininet commands we discussed in the section [Mininet commands](#Mininet-commands).

At long last, you have finished the Assignment 2! Now, if you execute `make`, you should see:
* The file `logs/monitor-output.txt` indicates that the monitor is successfully able to change the switch table entries at runtime. You will also observe that the monitor sees only `2-5` monitoring packets across the whole experiment. This shows that congestion occurred for a short period which was ultimately resolved.
* `iperf h1 h4` should indicate that the bandwidth between `h1` and `h4` is limited by the bottlenecked link `s1-s2`.
```
mininet> iperf h1 h4
*** Iperf: testing TCP bandwidth between h1 and h4
*** Results: ['925 Kbits/sec', '1.03 Mbits/sec']
```
* `iperf h2 h3` should indicate that the bandwidth between `h2` and `h3` is much higher now that the traffic `h2-->h3` is forwarded on a high-bandwidth route.
```
mininet> iperf h2 h3
*** Iperf: testing TCP bandwidth between h2 and h3
*** Results: ['25.0 Mbits/sec', '25.4 Mbits/sec']
```

## Deliverables
The following are the deliverables for this assignment:
* `switch.p4`
* `monitor-receive.py`
* Congestion graph for the [Task-1b](#Task-1b)

## Submission
To get the files from your VM, you can use the `vagrant scp` command ([link](https://stackoverflow.com/a/28359455/7263373)). You would have to use `default` as the `[vm_name]` in the command. The command works as follows:
```bash
# to transfer file from VM to your computer
vagrant scp default:path_to_file_on_vm destination_path_on_your_machine
```

Please send these deliverables to the teaching staff, Rohan (rohanbhatia@ucsb.edu), over email with the subject "YOUR FULL NAME: CS176B Assginemnt 2". Please cc Arpit (arpitgupta@ucsb.edu) and Punnal (punnalismail@ucsb.edu) to that email.

**Submissions not following the correct format will be penalized.**

## Grading Rubric
* Task 1a: 35 points
* Task 1b: 25 points
* Task 2: 40 points

## Acknowledement
This assignment builds up on SIGCOMM's [MRI tutorial](https://github.com/p4lang/tutorials/tree/master/exercises/mri).

<!-- links of various files below -->
[gq]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/graph_queues.py
[mr]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/monitor-receive.py
[s1rj]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/s1-runtime-init.json
[sm]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/start_mininet.py
[sp4]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/switch.p4
[sg]: https://github.com/SNL-UCSB/cs176b-assignments/blob/master/winter22/assignment2/queue_graph.png
