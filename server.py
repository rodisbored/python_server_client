#!/usr/bin/env python

# Author: Roderick Buenviaje
# Date: 01/27/2013
# Email: rod.buenviaje@gmail.com
# Feel free to copy and use, but please give credit if taking large chunks. This code is given as is.
# I haven't touched python in years, so I thought it would be good practice to just create a simple
# socket server/client

# Tested using Python 2.7.3 on Linux Mint 13

# This is a simple server that interacts with the messages provided by the client. It sends the client
# a user ID and the client then sends the server a message based on its user ID. The client can be expanded
# to keep sending messages with the same ID.

import socket 
import multiprocessing
import sys

class Server(object):
    def __init__(self, host, port):
        self.hostname = host
        self.port = port
        self.clientNumber = 0
        
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.hostname, self.port))
        except socket.error:
            print "Bind Failed"
            self.close();
            return
        # Queue currently only set to 10. Can be raised based on host system
        self.socket.listen(10)
        
        # Wait for accept, then send message and recv reply of user
        # Then repeat for any other users waiting to connect
        while 1:
            conn, address = self.socket.accept()
            process = multiprocessing.Process(target=handle, args=(conn, address, self.clientNumber))
            self.clientNumber += 1
            process.daemon = True
            process.start()
        
    def close(self):
        self.socket.close()
        
def handle(conn, address, clientNumber):
    try:
        conn.send(str(clientNumber))
        clientMessage = conn.recv(2048)
        # Should check for valid values inside clientMessage before printing out. But eh.
        print "User ID: %d" % int(clientMessage[5:13], 16)
        print "\tVersion: %d" % int(clientMessage[0], 16)
        print "\tMessage Type: %d" % int(clientMessage[1:5], 16)
        
        type = int(clientMessage[1:5], 16)
        if type == MessageType.binary:
            # change character into binary format and remove the 0b
            print "\tMessage: " + "".join(" %08d" % int(bin(ord(c))[2:]) for c in clientMessage[13:])
        elif type == MessageType.hex:
            # change character into hex format
            print "\tMessage: 0x" + " 0x".join("{0:x}".format(ord(c)) for c in clientMessage[13:])
        elif type == MessageType.string:
            # print string as is
            print "\tMessage: %s" % clientMessage[13:]
        elif type == MessageType.command:
            # perform command
            print "\t Command received."
            # if command succeeds/fails send message. Do not print to server
            # This can be used to update parameters on the server without having physical access to the server
            # Probably would want some security checking though...
            conn.send("Command success")
            #conn.send("Command failed")
        elif type == MessageType.reserved:
            #reserved for future use
            print "\t Reserved type."
        else:
            # unknown message type
            # Server doesn't need to know that the command was bunk, but the client should.
            conn.send("Unknown message type. Unable to process!")
    except socket.error:
        print "Server Send Error"

#My pseudo enum
class MessageType:
    binary = 1
    hex = 2
    string = 3
    command = 4
    reserved = 5


if __name__=='__main__':
    print "Initiating Server"
    
    # This is not set to be configurable like the client, since the server will usually always run on the
    # same host.  This should seldom be changed.
    HOST, PORT = "127.0.0.1", 8080

    server = Server(HOST, PORT)
    
    try:
        server.start()
    except KeyboardInterrupt: # Ctrl+C (^C)
        server.close()
        sys.exit(0)
