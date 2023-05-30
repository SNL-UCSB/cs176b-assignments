#!/usr/bin/env python

from scapy.all import *
from switch_entries import reprogram_all_switches
from shutil import copyfile
import json
import time


class OutHeader(Packet):
    name = "OutHeader"
    fields_desc = [IntField("swid", 0), IntField("qdepth", 0)]
    
    def extract_padding(self, p):
         return p, ""

    def guess_payload_class(self, payload):
        return Ether


def trigger_reprogram():
    print("#"*40)
    print("Changing switch entries...")
    print("#"*40)

    # create {}-runtime.json files
    for i in range(1, 5):
        sw_name = 's{}'.format(i)
        init_runtime_json = '{}-runtime-init.json'.format(sw_name)
        dynamic_runtime_json = '{}-runtime.json'.format(sw_name)
        copyfile(init_runtime_json, dynamic_runtime_json)

    # TODO: Modify the {}-runtime.json files with the new forwarding rules
    
    reprogram_all_switches()
    return


def handle_pkt_1(pkt):
    global OUT_DATA
    parsed_pkt = OutHeader(_pkt=bytes(pkt))

    if parsed_pkt[OutHeader].swid not in [1, 2, 3, 4]:
        return

    parsed_pkt.show2()
    
    data = '{},{},{}'.format(time.time() - START_TIME, parsed_pkt[OutHeader].swid, parsed_pkt[OutHeader].qdepth)
    OUT_DATA.append(data)
    
    sys.stdout.flush()
    return


def handle_pkt_2(pkt):
    global REPROGRAMMED
    parsed_pkt = OutHeader(_pkt=bytes(pkt))

    if parsed_pkt[OutHeader].swid not in [1, 2, 3, 4]:
        return
    parsed_pkt.show2()

    if not REPROGRAMMED:
        trigger_reprogram()
        REPROGRAMMED = True
    
    sys.stdout.flush()
    return


def main():
    # TODO: Modify prn argument in sniff function
    sniff(iface = ["monitor-eth1", "monitor-eth2", "monitor-eth3", "monitor-eth4"],
          prn=lambda x: handle_pkt_1(x), timeout=30)
    
    if len(OUT_DATA) > 1:
        working_dir = '/home/vagrant/cs176b-assignments/winter22/assignment2'
        with open('{}/logs/switch_stats.csv'.format(working_dir), 'w') as fp:
            fp.write('\n'.join(OUT_DATA))

    return



if __name__ == '__main__':
    REPROGRAMMED = False
    OUT_DATA = ["time,swid,qdepth"]
    START_TIME = time.time()
    main()
