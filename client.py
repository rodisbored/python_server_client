#!/usr/bin/env python

# Author: Roderick Buenviaje
# Date: 01/27/2013
# Feel free to copy and use, but please give credit if taking large chunks. This code is given as is.
# I haven't touched python in years, so I thought it would be good practice to just create a simple
# socket server/client

# Tested using Python 2.7.3 on Linux Mint 13

# This is a simple client that takes command line arguments and connects with the server of your choice
# It is currently configured with the server to use the localhost if no IP is provided
# If no arguments are given, the client just sends hello world to the server

import socket 
import sys
import argparse

from argparse import RawTextHelpFormatter

#char
version = 1
#u_int16
type = 0
#u_int32
userID = 0

DEFAULT_HOST, DEFAULT_PORT = "127.0.0.1", 8080

class Client(object):
    def __init__(self, host, port, type, automate, msg):
        self.hostname = host
        self.port = port
        self.type = type
        self.automate = automate
        self.msg = msg
        
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        
        try:
            self.socket.connect((self.hostname, self.port))
            userID = int(self.socket.recv(1024))
            print "User: %d" % userID
            
            # Send integer values as hex string
            # Error checking for valid values should be done before sending the message
            message = "%x%04x%08x%s" % (version, self.type, userID, self.msg)
            self.socket.send(message)
            
            #Can be expanded to keep sending/receiving messages between server
            #For my testing however, I am usually just sending once then closing the socket
            #An extra recv was placed here even in the case where there is no automation to check
            #for extra messages from the server
            if self.automate == False:
                # Client should keep running since we're doing local test
                # Open a new thread so you can keep sending messages here.  Then the recv thread will
                # keep getting any messages from the server
                while 1:
                    
                    print "Server Message: " + self.socket.recv(1024)
            else:
                print self.socket.recv(1024)
                
        # if just socket timeout, don't do anything. I want the client to just exit out
        except socket.timeout:
            self.close()
            return
        except socket.error:
            print "Unknown socket error"
            self.close()
            return
            
    def close(self):
        # Closes client socket
        self.socket.close()

#My pseudo enum
class MessageType:
    binary = 1
    hex = 2
    string = 3
    command = 4
    reserved = 5 # for future use
    
    
if __name__=="__main__":
    print "Initiating Client"
    
    parser = argparse.ArgumentParser(description="Send server a message", formatter_class=RawTextHelpFormatter)
    parser.add_argument("-ip", dest="IP", help="Server IP address to connect to. Ex. -ip 127.0.0.1")
    parser.add_argument("-p", dest="PORT", type=int, help="Server port to connect to. Ex. -p 8080")
    parser.add_argument("-t", dest="TYPE", type=int, help="Type of message to send. Ex. -t 3 \nBinary=1\nHex=2\nString=3\nCommand=4")
    parser.add_argument("-a", dest="AUTO", type=int, help="Used for spawning multiple clients. \nAuto=1\nAuto off=0")
    parser.add_argument("-s", dest="MSG", help="String message to send to the server.\nWill be converted to appropriate message type\nIf multiple words are provided, enclose them in quotes")
    
    # Not much error checking here.  More should be done
    args = parser.parse_args()
    
    if args.IP == None:
        serverAddress = DEFAULT_HOST
    else:
        serverAddress = args.IP
        
    if args.PORT == None:
        serverPort = DEFAULT_PORT
    else:
        serverPort = args.PORT
        
    if args.TYPE == None:
        type = MessageType.string
    else:
        type = args.TYPE
        
    if args.AUTO == None or args.AUTO == 1:
        automate = True
    else:
        automate = False
    
    if args.MSG == None:
        message = "hello world"
    else:
        message = args.MSG
        
    client = Client(serverAddress, serverPort, type, automate, message)
    
    try:
        client.start()
    except KeyboardInterrupt: # Ctrl+C (^C)
        client.close()
        sys.exit(0)
