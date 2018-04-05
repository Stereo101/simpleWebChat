import socket
import sys
import os
import threading
import time
import re

if(len(sys.argv) <= 1):
		print("Needs IP as arguement")
		sys.exit()
		
ip = sys.argv[1]

def loadCookie():
	global cookie
	cookie = "NULL"
	if(os.path.isfile("cookie")):
		cookie = open("cookie","r").read()
		print("Loaded cookie")
	return cookie	

socketSemaphore = threading.BoundedSemaphore(1)
cookie = loadCookie()

def saveCookie():
	global cookie
	open("cookie","w").write(cookie)
	print("saved cookie")

def main():
	postDaemon = threading.Thread(target=postReader,daemon=True)
	postDaemon.start()
	while True:
		m = input()
		reply = sendToSocket(m,ip)
		if(reply is not None):
			parseReply(reply)

def sendToSocket(message,ip):
	global cookie
	socketSemaphore.acquire()
	try:
		s = socket.socket()
		s.connect((ip,80))
		s.send(makePost(message,cookie).encode())
		reply = s.recv(1000)
	except ConnectionRefusedError:
		print("Server is offline")
		socketSemaphore.release()
		return None
	socketSemaphore.release()
	
	s_reply = reply.decode()
	m = re.search(r"Set-Cookie:(?P<cookie>[a-z0-9]+);",s_reply)
	if(m is not None):
		if(m.group("cookie") is not None):
				cookie = m.group("cookie")
				print("Cookie set to",cookie)
				saveCookie()
	return s_reply

def postReader():
	while True:
		time.sleep(1)
		r = sendToSocket("",ip)
		if(r is not None):
			parseReply(r)
		
def parseReply(r):
	messages = r.split("`")
	for i in range(1,len(messages)):
		
		print(messages[i].split("; ")[1])
	
def makePost(message,cookie):
	post = "POST / HTTP/1.1\r\nCookie: " + cookie + "\r\n\r\n" + message + "\r\n\r\n"
	return post

if __name__ == "__main__":
	main()