# Group: Riley Grimaud, Justine Kheiv, and Revel Etheridge
import argparse
import socket
import struct
import random

# Creates the packet
def create_packet(sequenceNum, ackNum, A, S, F, payload):                                                          #CHANGED 
    header = struct.pack('!IIcccI', sequenceNum, ackNum, A, S, F, len(payload))  # variable length for string         #NEEDS TO BE CHANGED
    packet = header + struct.pack(f'!{len(payload)}s', payload.encode('utf-8'))
    return packet

# Sends and Receives the packet from the server
def send_packet(s, sequenceNum, ackNum, A, S, F, payload, logfile):                                                         #CHANGED
    valid = True
    packet = create_packet(sequenceNum, ackNum, A, S, F, payload)                                                  #CHANGED
    s.sendall(packet) # Send the packet to the server

    # Receive the response header from the server
    server_packet = s.recv(struct.calcsize('!IIcccI'))
    sequenceNum, ackNum, A, S, F, lenPayload = struct.unpack('!IIcccI', server_packet)

    with open(logfile, 'a') as log:
        print(f"Received Data: sequenceNum: {sequenceNum} ackNum: {ackNum} A: {A} S: {S} F: {F}", file=log)

#            if ver == 17: # If version is 17, accept                                                                    ##NEEDS TO BE CHANGED; WE NO LONGER NEED TO WORRY 
#                                                                                                                        ##ABOUT VERSION NUMBER
#                with open(logfile, 'a') as log:
#                    print(f"VERSION ACCEPTED", file=log)
#            else: # Else, log the mismatch
#                with open(logfile, 'a') as log:
#                    print(f"VERSION MISMATCH", file=log)
#                valid = False

    # Receive the message from the server
    server_message = s.recv(lenPayload)
    message = struct.unpack(f'!{lenPayload}s', server_message)[0].decode('utf-8')
    # Log the message from the server
    with open(logfile, 'a') as log:
        print(f"Received Message {message}", file=log)
    if message == "SUCCESS":
        with open(logfile, 'a') as log:
            print(f"Command Successful", file=log)

    return message, valid



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for packet creation and sending.")
    parser.add_argument('-s', type=str, required=True, help='Server IP address')
    parser.add_argument('-p', type=int, required=True, help='Server port')
    parser.add_argument('-l', type=str, required=True, help='Path to the Log file')

    args = parser.parse_args()

    # connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.s, args.p))
        with open(args.l, 'a') as log:
            
            # Send the SYN packet
            seqNum = sequenceNumber = random.randint(0, 2147483647)                                             #CHANGED v
            ackNum = 0
            ack = 'N'
            syn = 'Y'
            fin = 'N'
            payload = ''
            print(f"Sending SYN Packet to server", file=log)
            response, is_accepted = send_packet(s, seqNum, ackNum, ack, syn, fin, payload, args.l) #args.l)?            #CHANGED ^

            #Get Response SYN-ACK                                                                                #changed; instead of going to send_packet function,
            server_packet = s.recv(struct.calcsize('!IIcccI'))                                                    #just handle sending and receiving in main 
            recvdSeqNum, recvdAckNum, A, S, F, lenPayload = struct.unpack('!IIcccI', server_packet)                                #for the syn-ack process
            server_message = s.recv(lenPayload)
            message = struct.unpack(f'!{lenPayload}s', server_message)[0].decode('utf-8')

            if (A == 'Y') & (S == 'Y') & (F == 'N'):
                 # Send the ACK packet
                seqNum = recvdAckNum                                                                                #CHANGED v
                ackNum = recvdSeqNum + 1                #since payload should be blank, adding it would only add 0 anyway
                ack = 'Y'
                syn = 'N'
                fin = 'N'
                payload = ''
                print(f"Sending ACK Packet to server", file=log)
                response, is_accepted = send_packet(s, seqNum, ackNum, ack, syn, fin, payload) #args.l)?            #CHANGED ^

            else:
                #loop back to send initial ACK


            
            if is_accepted:

                # Send the LIGHTON and LIGHTOFF commands
                response, is_accepted = send_packet(s, 1, "LIGHTON", args.l)
                response, is_accepted = send_packet(s, 2, "LIGHTOFF", args.l)
            
            with open(args.l, 'a') as log:
                print("Closing socket", file=log)
