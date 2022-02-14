#!/usr/bin/env python

import argparse
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')



def plot_results():
    working_dir = '/home/vagrant/cs176b-assignments/winter22/assignment2'
    csv_file = '{}/logs/switch_stats.csv'.format(working_dir)

    time_list, swid_list, qdepth_list = [], [], []
    
    # TODO: parse the CSV csv_file and extract
    # the first column in the time_list
    # the second column in the swid_list
    # the third column in the qdepth_list
    

    if len(swid_list) != 0:
        assert(all(x == 1 for x in swid_list))

    plt.plot(time_list, qdepth_list)
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Queue depth")
    plt.title("Congestion at the switch s1")
    plt.xlim(left=0, right=25)
    plt.savefig("queue_graph.png", facecolor='white')
    plt.show()
    return



if __name__ == "__main__":
    plot_results()
