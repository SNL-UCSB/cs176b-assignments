#!/usr/bin/env python

"""
Example to create a Mininet topology and connect it to the internet via NAT
"""

from p4_mininet import P4Switch, P4Host

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.topolib import TreeNet
from mininet.topo import Topo
from mininet.node import OVSController, OVSSwitch
from mininet.link import TCLink
from mininet.link import Intf, TCIntf
import math

import os
import subprocess

from p4runtime_switch import P4RuntimeSwitch
import p4runtime_lib.simple_controller

def configureP4Switch(**switch_args):
    """ Helper class that is called by mininet to initialize
        the virtual P4 switches. The purpose is to ensure each
        switch's thrift server is using a unique port.
    """
    if "sw_path" in switch_args and 'grpc' in switch_args['sw_path']:
        # If grpc appears in the BMv2 switch target, we assume will start P4Runtime
        class ConfiguredP4RuntimeSwitch(P4RuntimeSwitch):
            def __init__(self, *opts, **kwargs):
                kwargs.update(switch_args)
                P4RuntimeSwitch.__init__(self, *opts, **kwargs)

            def describe(self):
                print "%s -> gRPC port: %d" % (self.name, self.grpc_port)

        return ConfiguredP4RuntimeSwitch
    else:
        class ConfiguredP4Switch(P4Switch):
            next_thrift_port = 9090
            def __init__(self, *opts, **kwargs):
                global next_thrift_port
                kwargs.update(switch_args)
                kwargs['thrift_port'] = ConfiguredP4Switch.next_thrift_port
                ConfiguredP4Switch.next_thrift_port += 1
                P4Switch.__init__(self, *opts, **kwargs)

            def describe(self):
                print "%s -> Thrift port: %d" % (self.name, self.thrift_port)

        return ConfiguredP4Switch

def program_switch_p4runtime(net, sw_name):
    """ This method will use P4Runtime to program the switch using the
        content of the runtime JSON file as input.
    """
    sw_obj = net.get(sw_name)
    grpc_port = sw_obj.grpc_port
    device_id = sw_obj.device_id
    runtime_json = '{}-runtime.json'.format(sw_name)
#    self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
    with open(runtime_json, 'r') as sw_conf_file:
        outfile = './logs/runtime-requests/{}-p4runtime-requests.txt'.format(sw_name)
        p4runtime_lib.simple_controller.program_switch(
            addr='127.0.0.1:%d' % grpc_port,
            device_id=device_id,
            sw_conf_file=sw_conf_file,
            workdir=os.getcwd(),
            proto_dump_fpath=outfile)


def add_congestion_s1_s2(pps):
    info("*** Adding congestion at link s1-s2\n")
    with open(os.devnull, 'w') as fp:
        switch_cli = subprocess.Popen(["simple_switch_CLI", "--thrift-port", "9996"], stdin=subprocess.PIPE, stdout=fp, stderr=fp)
        switch_cli.communicate(input="set_queue_rate {} 1".format(int(pps)))
    return

def add_congestion_s1_s3(pps):
    info("*** Adding congestion at link s1-s3\n")
    with open(os.devnull, 'w') as fp:
        switch_cli = subprocess.Popen(["simple_switch_CLI", "--thrift-port", "9998"], stdin=subprocess.PIPE, stdout=fp, stderr=fp)
        switch_cli.communicate(input="set_queue_rate {} 1".format(int(pps)))
    return

def add_congestion_s2_s4(pps):
    info("*** Adding congestion at link s2-s4\n")
    with open(os.devnull, 'w') as fp:
        switch_cli = subprocess.Popen(["simple_switch_CLI", "--thrift-port", "9997"], stdin=subprocess.PIPE, stdout=fp, stderr=fp)
        switch_cli.communicate(input="set_queue_rate {} 2".format(int(pps)))
    return

    
class CoreP4Topo(Topo):
    host_objects = []

    def __init__(self, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)


        # These are the core P4 switches of the network
        switch1 = self.addSwitch('s1', thrift_port=9996)
        switch2 = self.addSwitch('s2', thrift_port=9997)
        switch3 = self.addSwitch('s3', thrift_port=9998)
        switch4 = self.addSwitch('s4', thrift_port=9999)

        # These are the end hosts in the network
        host1 = self.addHost('h1', ip='10.0.3.1/31', mac='08:00:00:00:03:01')
        host2 = self.addHost('h2', ip='10.0.3.2/31', mac='08:00:00:00:03:02')
        host3 = self.addHost('h3', ip='10.0.4.3/31', mac='08:00:00:00:04:03')
        host4 = self.addHost('h4', ip='10.0.4.4/31', mac='08:00:00:00:04:04')

        monitor = self.addHost('monitor')
        
        # Add these hosts to the global data structurewinter
        self.host_objects.append(host1)
        self.host_objects.append(host2)
        self.host_objects.append(host3)
        self.host_objects.append(host4)
        self.host_objects.append(monitor)

        # Add in the links between the P4 switches in the topology
        # TODO: add a link between s1 and s2
        # TODO: add a link between s1 and s3
        # TODO: add a link between s2 and s4

        # Connect each of the end hosts to the topology
        self.addLink(host1, switch3)
        self.addLink(host2, switch3)
        self.addLink(host3, switch4)
        self.addLink(host4, switch4)
        
        # Connect the monitor to each link
        self.addLink(monitor,switch1)
        self.addLink(monitor,switch2)
        self.addLink(monitor,switch3)
        self.addLink(monitor,switch4)

if __name__ == '__main__':


    # Configure the P4 Switch Class
    defaultSwitchClass = configureP4Switch(
        sw_path='simple_switch_grpc',
        json_path='build/monitor.json',
        log_console=True)
    
    # Create our P4 Topology, see topology.png
    topo = CoreP4Topo(4)

    # Create Mininet Network
    net = Mininet(topo = topo,
                  link = TCLink,
                  host = P4Host,
                  switch = defaultSwitchClass,
                  controller = None)
    
    # Start Network
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')

    monitor = net.get('monitor')

    h1.cmd('route add default gw 10.0.3.0 dev eth0')
    h1.cmd('arp -i eth0 -s 10.0.3.0 08:00:00:00:03:00')
    h2.cmd('route add default gw 10.0.3.3 dev eth0')
    h2.cmd('arp -i eth0 -s 10.0.3.3 08:00:00:00:03:00')
    h3.cmd('route add default gw 10.0.4.2 dev eth0')
    h3.cmd('arp -i eth0 -s 10.0.4.2 08:00:00:00:04:00')
    h4.cmd('route add default gw 10.0.4.5 dev eth0')
    h4.cmd('arp -i eth0 -s 10.0.4.5 08:00:00:00:04:00')
    
    # Add Control Plane rules for each switch
    program_switch_p4runtime(net, 's1')
    program_switch_p4runtime(net, 's2')
    program_switch_p4runtime(net, 's3')
    program_switch_p4runtime(net, 's4')
    
    # add_congestion_s1_s2(pps=0)
    # add_congestion_s1_s3(pps=0)
    # add_congestion_s2_s4(pps=0)

    ### Network Experiments ###
    def experiment():
        working_dir = '/home/vagrant/cs176b-assignments/spring23/assignment2'
        
        h3.cmd('iperf -s > {}/logs/h3-output.txt &'.format(working_dir))
        h2.cmd('iperf -c 10.0.4.3 > {}/logs/h2-output.txt &'.format(working_dir))
        monitor.cmd('{}/monitor_receive.py > {}/logs/monitor-output.txt &'.format(working_dir,working_dir))
        h4.cmd('{}/receive.py > {}/logs/h4-output.txt &'.format(working_dir, working_dir))
        h1.cmd('{}/client_send.py {} 80 > {}/logs/h1-output.txt &'.format(working_dir,h4.IP(),working_dir))
        
        return

    ###########################

    # Run Experiment Here
    # experiment()
    
    info( "*** Hosts are running\n" )
    info( "*** Type 'exit' or control-D to shut down network\n" )
    CLI( net )
    # Shut down NAT
    net.stop()
