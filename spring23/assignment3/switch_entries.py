#!/usr/bin/env python

import os
import argparse
from shutil import copyfile
import errno

import p4runtime_lib.simple_controller


def create_dir(path):
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return
                    

def program_switch_p4runtime(sw_name, grpc_port, device_id, grpc_server_ip='127.0.0.1'):
    """ This method will use P4Runtime to program the switch using the
        content of the runtime JSON file as input.
    """
    runtime_json = '{}-runtime.json'.format(sw_name)
    create_dir("logs/")
    copy_runtime_json = 'logs/{}-runtime-copy.json'.format(sw_name)
    copyfile(runtime_json, copy_runtime_json)

    with open(runtime_json, 'r') as sw_conf_file:
        outfile = './logs/{}-p4runtime-requests.txt'.format(sw_name)
        p4runtime_lib.simple_controller.program_switch(
            addr='{}:{}'.format(grpc_server_ip, grpc_port),
            device_id=device_id,
            sw_conf_file=sw_conf_file,
            workdir=os.getcwd(),
            proto_dump_fpath=outfile)
    return


def cleanup(sw_name, grpc_port, device_id, grpc_server_ip='127.0.0.1'):
    """ This method will use P4Runtime to remove all the entries added previously"""
    runtime_json = '{}-runtime.json'.format(sw_name)
    copy_runtime_json = 'logs/{}-runtime-copy.json'.format(sw_name)
    if not os.path.isfile(copy_runtime_json):
        return

    with open(copy_runtime_json, 'r') as sw_conf_file:
        outfile = './logs/{}-p4runtime-delete-requests.txt'.format(sw_name)
        p4runtime_lib.simple_controller.reset_switch(
            addr='{}:{}'.format(grpc_server_ip, grpc_port),
            device_id=device_id,
            sw_conf_file=sw_conf_file,
            workdir=os.getcwd(),
            proto_dump_fpath=outfile)
    return


def reprogram_all_switches(grpc_server_ip='127.0.0.1'):
    grpc_ports = [50051, 50052, 50053, 50054]
    device_ids = [0, 1, 2, 3]
    switch_names = ['s{}'.format(i) for i in range(1, 5)]
    for n, g, d in zip(switch_names, grpc_ports, device_ids):
        cleanup(n, g, d, grpc_server_ip)
        program_switch_p4runtime(n, g, d, grpc_server_ip)
    return


if __name__ == '__main__':
    reprogram_all_switches()
