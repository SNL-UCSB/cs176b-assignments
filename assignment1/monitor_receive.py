#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import PacketListField, ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

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


debug_pkt = None    

def main():
#    iface = 'eth0'
#    print "sniffing on %s" % iface
#    sys.stdout.flush()


    # TODO: update working_dir based on where you place these files
    working_dir = '/home/vagrant/cs176b-assignments-private/assignment1'
            
    f = open('{}/switch_stats.txt'.format(working_dir), 'w')

    def handle_pkt(pkt):
        print "got a packet"
        pkt.show2()

        def get_SI_header(l):
            for h in l:
                if h.option == 31:
                    print "Found SI header"
                    return h
            print "Could not find SI header for the following packet:"
            pkt.show2()
            return None
        SI_header = get_SI_header(pkt[IP].options)

        # record timestamp
        # record switch ID
        # record queue depth
        data = '{},{},{}\n'.format(pkt.time,SI_header.swtraces[0].swid,SI_header.swtraces[0].qdepth)

        f.write(data)
        f.flush()

        sys.stdout.flush()


    sniff(filter="udp",iface = ["eth0","monitor-eth1","monitor-eth2","monitor-eth3"],
          prn = lambda x: handle_pkt(x))
    f.close()
if __name__ == '__main__':
    main()
