# Group: Riley Grimaud, Justine Kheiv, and Revel Etheridge
import socket
import struct
import argparse
import random
from datetime import datetime
from gpiozero import LED # type: ignore
import time

led = LED(17)

def LightOn():
    led.on()

def LightOff():
    led.off()

def blink_led(b, d):
    for _ in range(b):
        LightOn()
        time.sleep(d / b)
        LightOff()
        time.sleep(d / b)
 
def unpack_packet(conn, header_format, logfile):
    client_packet = conn.recv(struct.calcsize(header_format))           # Receive the packet from the client

    #********************************UNPACK CLIENT'S HEADER********************************#
    recvdSequenceNum, recvdAckNum, A, S, F, payloadLen = struct.unpack(header_format, client_packet)

    dt = datetime.now()
    date_time = datetime.timestamp(dt)
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    with open(logfile, 'a') as log:                                     # Log the header information 
        print(f"\"RECV\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)


    #******************************RECEIVE PAYLOAD FROM CLIENT*************************#
    client_packet = conn.recv(payloadLen)
    payload = struct.unpack(f'{payloadLen}s', client_packet)

    return payload[0].decode('utf-8'), recvdSequenceNum, recvdAckNum, A, S, F, payloadLen


if __name__ == '__main__':

    #***************************PARSE ARGUMENTS***************************#
    parser = argparse.ArgumentParser(description="Server for turning on an LED.")
    parser.add_argument('-p', type=int, required=True, help='Port to listen on')
    parser.add_argument('-l', type=str, required=True, help='Log file')
    args = parser.parse_args()
    host = 'localhost'                  # Server's IP address: change to your machine's IP
    port = args.p                       # Port to listen on
    header_format = '!IIcccI'           # Specify the header format using "struct"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        
        while True:
            s.listen()                  # Listen for incoming connections
            conn, addr = s.accept()     # Accept the connection

            with conn:
                with open(args.l, 'a') as log: # Log the connection                                                 #NOT SURE WE NEED THIS ANYMORE                                  #ADD TIMESTAMP
                    dt = datetime.now()
                    date_time = datetime.timestamp(dt)
                    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                    with open(log, 'a') as log: 
                        print(f"Received connection from <{addr[0]}, {args.p}>", {timestamp}, file=log)
                
                #***************************RECEIVE SYN PACKET*******************************#
                A = 'N'
                S = 'N'
                F = 'N'
                
                while  ((A != 'N') & (S != 'Y') & (F != 'N')):
                    seqNum = random.randint(0, 2147483600)
                    try:
                        client_packet = conn.recv(struct.calcsize(header_format))  # Receive the packet from the client
                        recvdSequenceNum, recvdAckNum, A, S, F, payloadLen = struct.unpack(header_format, client_packet)

                        dt = datetime.now()
                        date_time = datetime.timestamp(dt)
                        timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                        with open(args.l, 'a') as log:
                            print(f"\"RECV\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)

                        client_packet = conn.recv(payloadLen)
                        payload = struct.unpack(f'{payloadLen}s', client_packet)

                        if S == 'N':
                            ackNum = recvdSequenceNum + 1 
                            A = 'N'
                            S = 'N'
                            F = 'N'
                            header = struct.pack(header_format, seqNum, ackNum, A, S, F, 0)
                            response_packet = header + "".encode('utf-8')
                            conn.sendall(response_packet)
                        pass
                    except:
                        print("Connection closed or an error occurred")
                        break


                #***************************SEND SYN-ACK PACKET*******************************#
                ackNum = recvdSequenceNum + 1 
                A = 'Y'
                S = 'Y'
                F = 'N'
                header = struct.pack(header_format, seqNum, ackNum, A, S, F, 0)
                response_packet = header + "".encode('utf-8')
                conn.sendall(response_packet)

                #Logging packet sending
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f"\"SEND\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)


                #******************************RECEIVE ACK PACKET**********************************#
                while  ((A != 'Y') & (S != 'Y') & (F != 'N')):
                    try:
                        client_packet = conn.recv(struct.calcsize(header_format))  # Receive the packet from the client
                        recvdSequenceNum, recvdAckNum, A, S, F, payloadLen = struct.unpack(header_format, client_packet)

                        dt = datetime.now()
                        date_time = datetime.timestamp(dt)
                        timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                        with open(args.l, 'a') as log:
                            print(f"\"RECV\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)

                        client_packet = conn.recv(payloadLen)
                        payload = struct.unpack(f'{payloadLen}s', client_packet)

                        if S == 'N':
                            ackNum = recvdSequenceNum + 1 
                            A = 'N'
                            S = 'N'
                            F = 'N'
                            header = struct.pack(header_format, seqNum, ackNum, A, S, F, 0)
                            response_packet = header + "".encode('utf-8')
                            conn.sendall(response_packet)
                        pass
                    except:
                        print("Connection closed or an error occurred")
                        break




                #***************************START MOTION SENSING SEQUENCE*********************#
                client_packet = conn.recv(struct.calcsize(header_format))  # Receive the packet from the client
                recvdSequenceNum, recvdAckNum, A, S, F, payloadLen = struct.unpack(header_format, client_packet)

                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(args.l, 'a') as log:
                    print(f"\"RECV\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)

                client_packet = conn.recv(payloadLen)
                payload = struct.unpack(f'{payloadLen}s', client_packet)

                digits = [int(digit) for digit in str(payload)]
                blinks = digits[0]
                duration = digits[1]
                #***************************ACKNOWLEDGE MOTION SENSING RECEPTION*********************# 
                ackNum = recvdSequenceNum + 1 
                header = struct.pack(header_format, seqNum, ackNum, A, S, F, 0)
                response_packet = header + f"{payload}".encode('utf-8')
                conn.sendall(response_packet)

                #***************************WAIT FOR MOTION DETECTION*********************#
                motion_packet = conn.recv(struct.calcsize(header_format))
                recvdSequenceNum, recvdAckNum, A, S, F, payloadLen = struct.unpack(header_format, motion_packet)

                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(args.l, 'a') as log:
                    print(f"\"RECV\": <{recvdSequenceNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)

                motion_packet = conn.recv(payloadLen)
                motion_payload = struct.unpack(f'{payloadLen}s', motion_packet)

                if motion_payload == ":MotionDetected":
                    blink_led(blinks, duration)





###########################OLD VERSION CODE#########################
#    if ver == 17:
#        with open(logfile, 'a') as log:
#            print(f"VERSION ACCEPTED", file=log)
#        client_packet = conn.recv(message_len)  # Receive the payload from the client
#
#        payload = struct.unpack(f'{message_len}s', client_packet)
#
#        return payload[0].decode('utf-8'), message_type
#    else: # Version is mismatched and don't receive the payload
#        with open(logfile, 'a') as log:
#            print(f"VERSION MISMATCH", file=log)
#        return None, message_type