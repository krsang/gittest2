# gittest2
네트워크프로그래밍 기말과제 저장소
#!/usr/bin/python3
import socket
import argparse
from struct import pack
#기본 접속 설정
DEFAULT_PORT = 69
BLOCK_SIZE = 512
DEFAULT_TRANSFER_MODE = 'octet'
TIMEOUT = 5  # Timeout value in seconds

OPCODE = {'RRQ': 1, 'WRQ': 2, 'DATA': 3, 'ACK': 4, 'ERROR': 5}
#에러 코드
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
# WRQ(Write Request) TFTP 메시지를 보내는 기능
def send_wrq(filename, mode, print_message=True):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    wrq_message = pack(format, OPCODE['WRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(wrq_message, server_address)
    if print_message:
        print(wrq_message)
# Read Request(RRQ) TFTP 메시지를 보내는 기능
def send_rrq(filename, mode, print_message=True):
    format = f'>h{len(filename)}sB{len(mode)}sB'
    rrq_message = pack(format, OPCODE['RRQ'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)
    sock.sendto(rrq_message, server_address)
    if print_message:
        print(rrq_message)
# 확인(ACK) TFTP 메시지를 보내는 기능
def send_ack(seq_num, server, print_message=True):
    format = f'>hh'
    ack_message = pack(format, OPCODE['ACK'], seq_num)
    sock.sendto(ack_message, server)
    if print_message:
        print(seq_num)
        print(ack_message)

# 명령줄
parser = argparse.ArgumentParser(description='TFTP client program')
parser.add_argument(dest="host", help="Server IP address", type=str)
parser.add_argument(dest="operation", help="get or put a file", type=str, choices=['get', 'put'])
parser.add_argument(dest="filename", help="name of file to transfer", type=str)
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()

#서버 포트 설정하기
server_port = args.port if args.port else DEFAULT_PORT

# UDP 소켓 설정하기
server_ip = args.host
server_address = (server_ip, 정
except socket.timeout:
    print("Timeout during data transfer")


sock.close()
