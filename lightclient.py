# Group: Riley Grimaud, Justine Kheiv, and Revel Etheridge
import argparse
import socket
import struct
import random

# Creates the packet
def create_packet(version, message_type, payload):
    header = struct.pack('!III', version, message_type, len(payload))  # variable length for string
    packet = header + struct.pack(f'!{len(payload)}s', payload.encode('utf-8'))
    return packet

# Sends and Receives the packet from the server
def send_packet(s, sequenceNum, ackNum, A, S, F, payload):                                                         #CHANGED
    valid = True
    packet = create_packet(sequenceNum, ackNum, A, S, F, payload)                                                  #CHANGED
    s.sendall(packet) # Send the packet to the server

    # Receive the response header from the server
    server_packet = s.recv(struct.calcsize('!III'))
    ver, message_type, message_len = struct.unpack('!III', server_packet)

    with open(logfile, 'a') as log:
        print(f"Received Data: version: {ver} message_type: {message_type} length: {message_len}", file=log)
    if ver == 17: # If version is 17, accept
        with open(logfile, 'a') as log:
            print(f"VERSION ACCEPTED", file=log)
    else: # Else, log the mismatch
        with open(logfile, 'a') as log:
            print(f"VERSION MISMATCH", file=log)
        valid = False
    # Receive the message from the server
    server_message = s.recv(message_len)
    message = struct.unpack(f'!{message_len}s', server_message)[0].decode('utf-8')
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
            print(f"Sending SYN Packet", file=log)
            # Send the SYN packet
            response, is_accepted = send_packet(s, 0, "HELLO", args.l)
            if is_accepted:

                # Send the LIGHTON and LIGHTOFF commands
                response, is_accepted = send_packet(s, 1, "LIGHTON", args.l)
                response, is_accepted = send_packet(s, 2, "LIGHTOFF", args.l)
            
            with open(args.l, 'a') as log:
                print("Closing socket", file=log)