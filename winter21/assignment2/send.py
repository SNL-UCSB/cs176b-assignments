#!/usr/bin/env python

import argparse
import pprint
from time import sleep


from scapy.all import sendp, sendpfast, hexdump, get_if_hwaddr
from scapy.all import Ether, IP, UDP



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", metavar="IP", type=str, help="IP addr of the receiver")
    parser.add_argument("time", metavar="Time", type=int, help="Time (in seconds) to send the traffic")
    parser.add_argument("--bw", metavar="Bandwidth", default=0.02, type=float, help="Bandwidth (in Mbps) of the traffic (default=20Kbps)")
    args = parser.parse_args()

    iface = "eth0"
    load = ''.join('f' for _ in range(1000))
    # Each packet has ~8Kb load
    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") / IP(dst=args.ip) / UDP(dport=4321, sport=1234) / load
    pkt.show2()

    num_packets = args.bw * 1000 * args.time / 8
    num_packets = int(1.1 * num_packets)

    summary = sendpfast(pkt, iface=iface, mbps=args.bw, loop=num_packets, file_cache=True, parse_results=True)
    del summary['warnings']
    print("Summary:")
    pprint.pprint(summary)    
    return



if __name__ == '__main__':
    main()
