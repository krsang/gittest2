#!/usr/bin/python3
import socket
import argparse
from struct import pack

DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'
TIMEOUT = 5  # Timeout value in seconds

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}

ERROR_CODE = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

def send_wrq(filename, mode, print_message=True):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)
    if print_message:
        print(wrq_message)

def send_rrq(filename, mode, print_message=True):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    if print_message:
        print(rrq_message)

def send_ack(seq_num, server, print_message=True):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    if print_message:
        print(seq_num)
        print(ack_message)

# parse command line arguments
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str, choices=['get', 'put'])
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()

# Set the server port
server_port = args.port if args.port else DEFAULT_PORT

# Create a UDP socket
server_ip = args.host
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set socket timeout
sock.settimeout(TIMEOUT)

mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

# Send RRQ or WRQ message based on the operation
if operation == 'put':
    send_wrq(filename, mode, print_message=False)
else:
    send_rrq(filename, mode, print_message=False)

# Open a file with the same name to save data from the server
file = open(filename, 'wb')
expected_block_number = 1

try:
    while True:
        # receive data from the server
        data, server_new_socket = sock.recvfrom(516)
        opcode = int.from_bytes(data[:2], 'big')

        # initialize file_block here
        file_block = b''

        # check message type
        if opcode == OPCODE['DATA']:
            block_number = int.from_bytes(data[2:4], 'big')
            if block_number == expected_block_number:
                send_ack(block_number, server_new_socket, print_message=False)
                file_block = data[4:]
                file.write(file_block)
                expected_block_number += 1
                print(file_block.decode())
            else:
                send_ack(block_number, server_new_socket, print_message=False)

        elif opcode == OPCODE['ERROR']:
            error_code = int.from_bytes(data[2:4], byteorder='big')
            print(ERROR_CODE[error_code])
            break

        if len(file_block) < BLOCK_SIZE:
            file.close()
            print("File transfer successful.")  # Add this line for success
            break
except socket.timeout:
    print("Timeout during data transfer")

# Close the socket at the end of the transfer
sock.close()