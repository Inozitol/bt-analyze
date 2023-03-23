import argparse
import random
import string
import sys
import socket
import bencoder
import time


def send_dht(address, port, dht, interval):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    data = None
    if dht == 'ping':
        data = {b'a': {b'id': bytes.fromhex('afea60fea601231a113dafea60fea601231a113d')},
                b'q': b'ping',
                b't': b'',
                b'y': b'q'}
    elif dht == 'find_node':
        data = {b'a': {b'id': bytes.fromhex('afea60fea601231a113dafea60fea601231a113d'),
                       b'target': bytes.fromhex('3c68a8e201ef8bfc4f057866d77af51a199cb227')},
                b'q': b'find_node',
                b't': b'',
                b'y': b'q'}
    elif dht == 'get_peers':
        data = {b'a': {b'id': bytes.fromhex('afea60fea601231a113dafea60fea601231a113d'),
                       b'info_hash': bytes.fromhex('3c68a8e201ef8bfc4f057866d77af51a199cb227')},
                b'q': b'get_peers',
                b't': b'',
                b'v': bytes.fromhex('4c54012f'),
                b'y': b'q'}

    while True:
        data[b't'] = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
        payload = bencoder.encode(data)
        s.sendto(payload, (address, port))
        print(f"Sent {dht} message")
        time.sleep(interval/1000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MLDHT packets sender')
    parser.add_argument('--address',
                        help='Address or hostname of MLDHT client', required=True)
    parser.add_argument('--port',
                        help='Port of MLDHT client', required=True)
    parser.add_argument('--dht-type',
                        help='What kind of DHT messages to send', required=True)
    parser.add_argument('--period',
                        help='Period in ms of sent messages', required=True)

    args = parser.parse_args()

    address = args.address
    port = int(args.port)
    dht = args.dht_type
    period = int(args.period)

    send_dht(address, port, dht, period)

    sys.exit(0)
