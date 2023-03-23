import argparse
import os
import sys
import struct

from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP

import bencoder

import matplotlib.pyplot as plt

my_id = None
query_bit_distance = []
response_bit_distance = []
count = 0

def compact2tuple(record_bytes):
    if len(record_bytes) != 26:
        return None

    node_id = record_bytes[:20]
    ip_bytes = record_bytes[-6:-2]
    port_bytes = record_bytes[-2:]
    ip_string = str(ip_bytes[0]) + '.' + str(ip_bytes[1]) + '.' + \
                str(ip_bytes[2]) + '.' + str(ip_bytes[3])
    port_int = int.from_bytes(port_bytes, "big")

    return node_id, ip_string, port_int


def process_query(bencoded):
    global my_id
    global query_bit_distance

    if my_id is None:
        my_id = bencoded[b'a'][b'id']

    if bencoded[b'q'] == b'get_peers':
        xor_bytes = bytes([a ^ b for a, b in zip(my_id, bencoded[b'a'][b'info_hash'])])
        xor_int = int.from_bytes(xor_bytes, "big")
        query_bit_distance.append(xor_int.bit_length() - 1)


def process_response(bencoded):
    global my_id
    global response_bit_distance

    if b'nodes' in bencoded[b'r']:
        compact_nodes = bencoded[b'r'][b'nodes']
        for i in range(0, len(compact_nodes), 26):
            node = compact_nodes[i:i + 26]
            record = compact2tuple(node)

            if record[1] == '109.105.39.18' or record[1] == '192.168.0.42':
                print(f'My IP hit on packet {count}')

            xor_bytes = bytes([a ^ b for a, b in zip(my_id, record[0])])
            xor_int = int.from_bytes(xor_bytes, "big")

            response_bit_distance.append(xor_int.bit_length() - 1)


def process_pcap(filename):
    global count
    print(f'Opening {filename}')

    for (pkt_data, pkt_meta,) in RawPcapReader(filename):
        count += 1
        eth_pkt = Ether(pkt_data)
        if 'type' not in eth_pkt.fields:
            continue

        if eth_pkt.type != 0x0800:
            continue

        ip_pkt = eth_pkt[IP]
        if ip_pkt.proto != 0x11:
            continue

        udp_pkt = ip_pkt[UDP]

        payload = udp_pkt.payload.load
        if payload[0] != 100:
            continue

        try:
            bencoded = bencoder.decode(udp_pkt.payload.load)
        except IndexError:
            continue
        if bencoded[b'y'] == b'q':
            process_query(bencoded)
        if bencoded[b'y'] == b'r':
            process_response(bencoded)

    print(f"Contains {count} packets")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DHT Pcap analyzer')
    parser.add_argument('--pcap', metavar='<pcap file name>',
                        help='pcap with DHT communication', required=True)
    args = parser.parse_args()

    file_name = args.pcap
    if not os.path.isfile(file_name):
        print(f'"{file_name}" does not exist', file=sys.stderr)
        sys.exit(-1)

    process_pcap(file_name)

    print(response_bit_distance)
    plt.hist(response_bit_distance)
    plt.show()
    sys.exit(0)
