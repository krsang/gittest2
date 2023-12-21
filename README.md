# gittest2
네트워크프로그래밍 기말과제 저장소
#!/usr/bin/python3
import socket
import argparse
from struct import pack
import os
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
server_address = (server_ip, server_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set socket timeout
sock.settimeout(TIMEOUT)

mode = DEFAULT_TRANSFER_MODE
operation = args.operation
filename = args.filename

# 변수에 따라 wrq rrq 설정
if operation == 'put':
    send_wrq(filename, mode, print_message=False)
else:
    send_rrq(filename, mode, print_message=False)

# 같은 이름의 파일을 열어 서버에서 데이터를 저장합니다.
file = None  # Initialize file to None
expected_block_number = 1

file_found_before_transfer = False

# 파일이 이미 로컬에 존재하는지 나타내는 플래그
file_exists_locally = os.path.exists(filename)

# 작업을 기반으로 RRQ/WRQ 메시지를 보내기 전에 파일을 엽니다
try:
    if operation == 'get':
        if file_exists_locally:
            file = open(filename, 'wb')  # Open the file in binary write mode
            send_rrq(filename, mode, print_message=False)
            file_found_before_transfer = True
            print(f"File '{filename}' found on the server. Initiating transfer.")
        else:
            raise FileNotFoundError(f"File '{filename}' not found locally.")
    elif operation == 'put':
        if not file_exists_locally:
            file = open(filename, 'xb')  # 'x' flag ensures that the file is created, raises FileExistsError if it already exists
            send_wrq(filename, mode, print_message=False)
            print(f"File '{filename}' created locally. Initiating transfer.")
            file_found_before_transfer = True  # Set to True for 'put' operation
        else:
            raise FileExistsError(f"File '{filename}' already exists locally. Transfer aborted.")
except FileNotFoundError as e:
    print(e)
except FileExistsError as e:
    print(e)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
file_found = False
#실행프로세스 
try:
    while True:
        # 서버로부터 정보를 받습니다.
        data, server_new_socket = sock.recvfrom(516)
        opcode = int.from_bytes(data[:2], 'big')

        # initialize file_block here.
        file_block = b''

        # 메세지타입을 확인합니다다
        if opcode == OPCODE['DATA']:
            block_number = int.from_bytes(data[2:4], 'big')
            if block_number == expected_block_number:
                send_ack(block_number, server_new_socket, print_message=False)
                file_block = data[4:]
                if file is None:
                    file = open(filename, 'wb')  # Open the file in binary write mode
                file.write(file_block)
                expected_block_number += 1
                print(file_block.decode())
            else:
                send_ack(block_number, server_new_socket, print_message=False)

        #타입이 레어이면 처리하는 구간입니다.
        elif opcode == OPCODE['ERROR']:
            error_code = int.from_bytes(data[2:4], byteorder='big')
            if error_code == 1 and file is not None:  # File not found (and the file was opened)
                print(f"File '{filename}' not found on the server. Transfer aborted.")
                file.close()
                os.remove(filename)  # Remove the created file
            else:
                print(ERROR_CODE[error_code])
            break
        #수신된 블록의 사이즈를 측정하여 알맞게 처리합니다.
        if len(file_block) < BLOCK_SIZE:
            if file is not None:
                file.close()
                if file_block and operation == 'get':
                    if file_found_before_transfer:
                        print(f"File '{filename}' transfer successful.")
                    else:
                        print(f"File '{filename}' transfer incomplete.")
                elif not file_found_before_transfer:
                    print(f"File '{filename}' not found on the server.")
except socket.timeout:
    print("Timeout during data transfer")

# 실행을 종료합니다.
sock.close()
