import os
import socket
import time
from threading import Thread
from functions import *

iface = ""
addr = ""
bcast = ""
port = 12345
homies = [] # [ [IP_a, timeout_a] , [IP_b, timeout_b] ]
beacon_interval = 5 #beacon sent every 5s
homie_timeout_intervals = 3 #beacon intervals until timeout
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
'''
THREE DIFFERENT THREADS:

 	- SOCKET THREAD: LISTENS FOR UDP MESSAGES

	- HTTP SERVER LISTENING ON LOOPBACK INTERFACE, AS AN API TO
	  INTERACT WITH THE PROGRAM (GET UPDATED HOMIE LIST, SEND FILE SHARING
	  REQUEST, ETC.)

	- BEACON THREAD: PERIODICALLY (beacon_interval) SENDS HOMIE DISCOVERY REQUESTS

	- HOMIE CONTROL THREAD: REMOVES HOMIE FROM LIST IF NO BEACONS ARE
	  RECEIVED DURING homie_timeout_intervals BEACON INTERVALS
'''

def main():
	init_socket() #configures and initializes socket 
	socket_thread = Thread(target=socket_listen)
	socket_thread.start()
	#http_thread = Thread(target=init_http)
	#http_thread.start()
	beacon_thread = Thread(target=periodic_beacon)
	beacon_thread.start()
	homie_control_thread = Thread(target=homie_control)
	homie_control_thread.start()
	
if __name__=='__main__':
	main()
