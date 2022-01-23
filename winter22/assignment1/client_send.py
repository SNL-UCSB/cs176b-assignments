#!/usr/bin/env python

import argparse
import sys
import socket
import random
import struct
import os

from scapy.all import sendp, send, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP
from scapy.all import IntField, FieldListField, FieldLenField, ShortField, PacketListField
from scapy.layers.inet import _IPOption_HDR

from time import sleep

class SwitchTrace(Packet):
    fields_desc = [ IntField("swid", 0),
                  IntField("qdepth", 0)]
    def extract_padding(self, p):
                return "", p

class IPOption_SI(IPOption):
    name = "SI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swtraces",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    PacketListField("swtraces",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]


def main():

    if len(sys.argv)<3:
        print 'pass 2 arguments: <destination> "<message>"'
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])

    iface = "eth0"

    src_port = random.randrange(1024,30000)
    dst_port = random.randrange(1024,30000)
    
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") / IP(
        dst=addr, options = IPOption_SI(count=0, swtraces=[])) / UDP(dport=random.randrange(1024,30000), sport=random.randrange(1024,30000))

    pkt.show2()
    try:
        sendp(pkt, iface=iface, loop=1)
    except KeyboardInterrupt:
        raise


if __name__ == '__main__':
    main()
