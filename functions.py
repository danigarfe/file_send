import os
import socket
import time
from server_init import *

def init_socket():
	global client
	client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(('',port))

def socket_listen():
	global client, beacon_interval
	get_info()
	print("[SOCKET] Using interface " + iface)
	print("[SOCKET] Listening on address " + addr)
	print("[SOCKET] Port: " + str(port))
	print("[SOCKET] Beacon interval: " + str(beacon_interval) + "s")
	print("[SOCKET] A homie will be removed if not receiving beacon during " + str(beacon_interval*homie_timeout_intervals) + "s")
	print()
	print()
	print()
	while True:
		data, (rcvIP, rcvport) = client.recvfrom(1024)
		handler(data, rcvIP, rcvport)

#MESSAGE STRUCTURE: A/B
#MESSAGE TYPES:
# 1/1 => FILE TRANSFER REQUEST 
# 2/1 => FILE TRANSFER ACCEPT
# 2/2 => FILE TRANSFER DENY
# 3/1 => BEACON 

def handler(data, IP, port):
	global homies, client, addr
	try:
		request = str(data)[2:-1]
		sp  = request.split('/')
		Rtype = int(sp[0])
		Rsubtype = int(sp[1])
	except:
		print("Invalid request received: " + str(data))
		return
	if (Rtype==1 and Rsubtype==1):
		if str(IP)==addr:
			print("[REQUEST] YOU SENT A FILE TRANSFER REQUEST")
		else:		
			print("[REQUEST] " + str(IP) + " SENT YOU A FILE TRANSFER REQUEST")
			#client.sendto(b'2/1', (bcast, port)) 
	if (Rtype==3 and Rsubtype==1):
		if str(IP)!=addr:		
			print("[BEACON] " + str(IP))
			found = False
			for h in homies:
				if h[0]==str(IP):
					found = True
					h[1]=0 #restart timeout counter
			if not found:
				homies.append([str(IP), 0])


def get_info():
	global iface, addr, bcast
	getiface_command = "ip link show | grep 2: | cut -d ':' -f 2 | cut -d ' ' -f 2"
	iface = os.popen(getiface_command).read()
	iface = iface[0:-1]
	getaddr_command = "(ifconfig " + iface + ") | grep inet | cut -d 't' -f 2 | cut -d ' ' -f 2"
	addr = os.popen(getaddr_command).read()
	addr = addr[0:-1]
	getbcast_command = "(ifconfig " + iface + ") | grep broadcast | cut -d 't' -f 4 | cut -d ' ' -f 2"
	bcast = os.popen(getbcast_command).read()
	bcast = bcast[0:-1]

def periodic_beacon():
	global client, bcast, port, beacon_interval
	while True:
		time.sleep(beacon_interval)
		client.sendto(b'3/1', (bcast, port))

def homie_control():
	global homies, beacon_interval, homie_timeout_intervals
	while True:
		time.sleep(beacon_interval)
		print(homies)
		for h in homies:
			h[1] = h[1] + 1
			if h[1] == homie_timeout_intervals:
				homies.remove(h)
