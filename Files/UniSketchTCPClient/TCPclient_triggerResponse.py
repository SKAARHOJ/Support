#!/usr/bin/env python3

import sys
import socket
import fcntl, os
import errno
from time import sleep
import time
import re


HOST = '192.168.10.99'  # Raw Panel server IP address
PORT = 9923        # Port used by Raw Panel


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(0.5)

busy = False	# This keeps track of the busy/ready state of the client. We can use this to make sure we are not spamming it with data
colorV = 0

while True:
	try:
		# s is the TCP socket connected to the server
		data = s.recv(1024).strip()
	except socket.timeout:
		pass
	else:
		if data != b'':
			for line in data.split(b"\n"):
				outputline = "ClearDisplays\n"
				print("Server {} sent: '{}<NL>'".format(HOST, line.decode('ascii')))

				if line == b"BSY":
					busy = True
				if line == b"RDY":
					busy = False

				if not busy:
					match = re.search(r"^HWC#([0-9]+)(.([0-9]+)|.*)=Down$", line.decode('ascii'))
					if match:
						print("Sending a bunch of key change commands:\n")
						for a in range (1, 40):
							line = "HWC#{}={}\n".format(a,4)
							outputline = outputline+line
						#	s.sendall(line.encode('ascii'))
							
							line = "HWCc#{}={}\n".format(a,colorV | 0x80)
							outputline = outputline+line
						#	s.sendall(line.encode('ascii'))

							line = "HWCt#{}={}\n".format(a,colorV | 0x80)
							outputline = outputline+line
						#	s.sendall(line.encode('ascii'))

						colorV = (colorV + 1)%17

						s.sendall(outputline.encode('ascii'))
		else:
			print("{} closed".format(HOST))
			break
