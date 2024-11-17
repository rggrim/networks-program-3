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

    return payload[0].decode('utf-8')


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
                    print(f"Received connection from <{addr[0]}, {args.p}>", {timestamp}, file=log)
                
                #***************************RECEIVE SYN PACKET*******************************#
                A = 'N'
                S = 'N'
                F = 'N'

                while  ((A != 'Y') & (S != 'N') & (F != 'N')):
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


                        pass
                    except:
                        print("Connection closed or an error occurred")
                        break


                #***************************SEND SYN-ACK PACKET*******************************#



                #***************************RECEIVE ACK PACKET*******************************#



                #***************************START MOTION SENSING SEQUENCE*********************#
                while True:
                    try:
                        # Receive and unpack packet using the unpack_packet function
                        payload_string = unpack_packet(conn, header_format, args.l)
                        pass
                    except:
                        print("Connection closed or an error occurred")
                        break

                    #if message_type == 0: # If the message type is 0, send the HELLO response
                    #    header = struct.pack(header_format, 17, 0, len("HELLO"))
                    #    response_packet = header + "HELLO".encode('utf-8')

                    # If the message type is 1 or 2, check if the payload is LIGHTON or LIGHTOFF
                    elif message_type in [1, 2]:
                        # If the command is valid, execute the command
                        if payload_string in ["LIGHTON", "LIGHTOFF"]:
                            dt = datetime.now()
                            date_time = datetime.timestamp(dt)
                            timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                            with open(args.l, 'a') as log:
                                print(f"EXECUTING SUPPORTED COMMAND: {payload_string}", {timestamp}, file=log)
                            if payload_string == "LIGHTON":
                                LightOn() # Turn on the light
                            else:
                                LightOff() # Turn off the light
                            header = struct.pack(header_format, 17, 1, len("SUCCESS"))
                            response_packet = header + "SUCCESS".encode('utf-8')
                        else:
                            dt = datetime.now()
                            date_time = datetime.timestamp(dt)
                            timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                            with open(args.l, 'a') as log:
                                print(f"IGNORING UNKNOWN COMMAND: {payload_string}", {timestamp}, file=log)
                    else:
                        break # close connection because version mismatched

                    with open(args.l, 'a') as log:
                        dt = datetime.now()
                        date_time = datetime.timestamp(dt)
                        timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                        print(f"RETURNING SUCCESS", {timestamp}, file=log)
                    # Send the response packet to the client
                    conn.sendall(response_packet)




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