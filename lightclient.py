# Group: Riley Grimaud, Justine Kheiv, and Revel Etheridge
import argparse
import socket
import struct
import random
from gpiozero import MotionSensor #type: ignore
from datetime import datetime

# allows control of the GPIO pins on the Raspberry Pi
PIR_PIN = 4

# Creates the packet
def create_packet(sequenceNum, ackNum, A, S, F, payload):                                                          #CHANGED 
    #header = struct.pack('!IIcccI', sequenceNum, ackNum, A, S, F, len(payload))  # variable length for string         #NEEDS TO BE CHANGED
    
    #packing the sequence number (32 bits) and acknowledgement number (32 bits)
    header += struct.pack('!I', sequenceNum)
    header += struct.pack('!I', ackNum)

    #packing the "Not Used" section with 3 bytes (29 bits) of 0's
    header += struct.pack('!I', 0)[:3]

    #packing each flag (one byte each)
    header += struct.pack("!c", A)
    header += struct.pack("!c", S)
    header += struct.pack("!c", F)

    #packing the length of the payload
    header += struct.pack("!c", len(payload))

    #packing the payload
    packet = header + struct.pack(f'!{len(payload)}s', payload.encode('utf-8'))
    return packet

# Sends and Receives the packet from the server
def send_packet(s, sequenceNum, ackNum, A, S, F, payload, logfile):                                                         #CHANGED
    
    #"RECV" <Sequence Number> <Acknowledgement Number> ["ACK"] ["SYN"] ["FIN"]
    #"SEND" <Sequence Number> <Acknowledgement Number> ["ACK"] ["SYN"] ["FIN"]
    packet = create_packet(sequenceNum, ackNum, A, S, F, payload)                                                  #CHANGED
    s.sendall(packet) # Send the packet to the server
   
    #Logging packet sending
    dt = datetime.now()
    date_time = datetime.timestamp(dt)
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    with open(logfile, 'a') as log: 
        print(f"\"SEND\": <{sequenceNum}> <{ackNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=logfile)

    # Receive the response header from the server
    server_packet = s.recv(struct.calcsize('!IIcccI'))
    sequenceNum, ackNum, A, S, F, lenPayload = struct.unpack('!IIcccI', server_packet)

    #Logging packet reception
    dt = datetime.now()
    date_time = datetime.timestamp(dt)
    timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
    with open(logfile, 'a') as log:
        print(f"\"RECV\": <{sequenceNum}> <{ackNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=logfile)

    server_message = s.recv(lenPayload)
    message = struct.unpack(f'!{lenPayload}s', server_message)[0].decode('utf-8')

    return message, sequenceNum, ackNum, A, S, F, lenPayload



if __name__ == '__main__':

    #**************************ACCEPT ARGS***************************#
    parser = argparse.ArgumentParser(description="Client for packet creation and sending.")
    parser.add_argument('-s', type=str, required=True, help='Server IP address')
    parser.add_argument('-p', type=int, required=True, help='Server port')
    parser.add_argument('-l', type=str, required=True, help='Path to the Log file')

    args = parser.parse_args()

    #************************CONNECT TO SERVER**********************#
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.s, args.p))
        with open(args.l, 'a') as log:

            A = 'N'
            S = 'N'
            F = 'N'
            recvdAckNum = 0

            while ((A != 'Y') & (S != 'Y') & (F != 'N')):
                #*****************SENDING SYN PACKET*****************#
                seqNum = random.randint(0, 2147483600)
                ackNum = 0
                ack = 'N'
                syn = 'Y'
                fin = 'N'
                payload = ''
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                #with open(log, 'a') as log: 
                #    print(f"\"SEND\": <{seqNum}> <{ackNum}> [\"{ack}\"] [\"{syn}\"] [\"{fin}\"]", {timestamp}, file=log)                 #CHANGED ^
                header = struct.pack('!IIcccI', seqNum, ackNum, ack, syn, fin, len(payload))                                #NEEDS TO BE CHANGED
                packet = header + struct.pack(f'!{len(payload)}s', payload.encode('utf-8'))
                s.sendall(packet) # Send the packet to the server
                
                #Logging packet sending
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f"\"SEND\": <{seqNum}> <{ackNum}> [\"{ack}\"] [\"{syn}\"] [\"{fin}\"]", {timestamp}, file=log)

                #*******************RECEIVING SYN-ACK*********************#                                                                        #changed; instead of going to send_packet function,
                server_packet = s.recv(struct.calcsize('!IIcccI'))                                                    #just handle sending and receiving in main 
                recvdSeqNum, recvdAckNum, A, S, F, lenPayload = struct.unpack('!IIcccI', server_packet)                #for the syn-ack process
                server_message = s.recv(lenPayload)
                message = struct.unpack(f'!{lenPayload}s', server_message)[0].decode('utf-8')                                  #NEED TO MANUALLY ADD LOG ENTRY
                
                #Logging packet sending
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f"\"RECV\": <{recvdSeqNum}> <{recvdAckNum}> [\"{A}\"] [\"{S}\"] [\"{F}\"]", {timestamp}, file=log)

            #***********************SENDING ACK PACKET**********************#
            seqNum = recvdAckNum 
            ackNum = recvdSeqNum + 1                
            ack = 'Y'
            syn = 'N'
            fin = 'N'
            payload = ''

            dt = datetime.now()
            date_time = datetime.timestamp(dt)
            timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
            with open(log, 'a') as log: 
                print(f"\"SEND\": <{seqNum}> <{ackNum}> [\"{ack}\"] [\"{syn}\"] [\"{fin}\"]", {timestamp}, file=log)
            response, recvdSeqNum, recvdAckNum, A, S, F, lenPayload = send_packet(s, seqNum, ackNum, ack, syn, fin, payload, args.l) #args.l)?            #CHANGED ^

            #********************INITIATE CONTINUOUS MOTION SENSING******************#
            stillRunning = True

            while stillRunning:

                #************************SEND BLINKS AND DURATION********************#
                seqNum = recvdAckNum
                ackNum = recvdSeqNum + 1 + lenPayload
                ack = 'Y'
                syn = 'N'
                fin = 'N'
                payload = '44'
                response, recvdSeqNum, recvdAckNum, A, S, F, lenPayload = send_packet(s, seqNum, ackNum, ack, syn, fin, payload, args.l)

                #*************************START MOTION SENSOR*************************#
                pir = MotionSensor(PIR_PIN)
                pir.wait_for_motion()
                print("You moved")

                #need to log motion detected.
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f"{timestamp} :MotionDetected", file=log)

                #********************ALERT SERVER MOTION DETECTED**********************#
                seqNum = recvdAckNum
                ackNum = recvdSeqNum + 1 + lenPayload
                ack = 'Y'
                syn = 'N'
                fin = 'N'
                payload = ':MotionDetected'
                response, recvdSeqNum, recvdAckNum, A, S, F, lenPayload = send_packet(s, seqNum, ackNum, ack, syn, fin, payload, args.l)

                #pir.wait_for_no_motion()

                #**************************CLOSE CONNECTION***************************#
                seqNum = recvdAckNum
                ackNum = recvdSeqNum + 1 + lenPayload
                ack = 'N'
                syn = 'N'
                fin = 'Y'
                payload = ':Interaction with completed'
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f":Interaction with completed",{timestamp},  file=log)
                response, recvdSeqNum, recvdAckNum, A, S, F, lenPayload = send_packet(s, seqNum, ackNum, ack, syn, fin, payload, args.l) #args.l)?            #CHANGED ^



            with open(args.l, 'a') as log:
                dt = datetime.now()
                date_time = datetime.timestamp(dt)
                timestamp = date_time.strftime("%Y-%m-%d-%H-%M-%S")
                with open(log, 'a') as log: 
                    print(f"Closing socket",{timestamp}, file=log)






#            if ver == 17: # If version is 17, accept                                                                    ##NEEDS TO BE CHANGED; WE NO LONGER NEED TO WORRY 
#                                                                                                                        ##ABOUT VERSION NUMBER
#                with open(logfile, 'a') as log:
#                    print(f"VERSION ACCEPTED", file=log)
#            else: # Else, log the mismatch
#                with open(logfile, 'a') as log:
#                    print(f"VERSION MISMATCH", file=log)
#                valid = False

    # Receive the message from the server