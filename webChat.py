import socket
import threading
import re
import time
import random

indexHTML_bytes = open("index.html","r").read().encode("utf-8")
postSemaphore = threading.BoundedSemaphore(1)
postArr = []
cookieDict = {}

def generateCookie():
	i = random.randint(1,200000000000)
	t = time.time()
	cookieDict[str(i)] = t
	print("cookie",i,"added at time",t)
	return str(i)

def formatHTTP(response,cookie=None,skipCookie=False):
	#httpOK = "HTTP/1.1 200 OK\r\nContent-Length:"
	httpOK = "HTTP/1.1 200 OK\r\n"
	if(cookie is None and skipCookie is False):
		httpOK += "Set-Cookie:" + generateCookie() + "\r\n"
	httpOK += "\r\n"
	#l = len(response)
	header = (httpOK).encode("utf-8")
	return header + response

	
def startServer(address,port):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind((address,port))
	s.listen(5)
	print("Server started")
	while True:
		(client,address) = s.accept()
		threading.Thread(target=connectionHandler,args=[client,address]).start()
		
		
def connectionHandler(client,address):
	bytes = client.recv(10000)
	request = bytes.decode("utf-8")
	#print(request)
	m = re.search(r"(?P<type>GET|POST) (?P<resource>[a-zA-Z/\.]+) HTTP/1.1",request)
	
	type = ""
	group = ""
	cookie = -1
	if(m is not None):
		if(m.group("type") is not None):
			type = m.group("type")
		if(m.group("resource") is not None):
			resource = m.group("resource")
		
	#print("Resource is \"" +resource+"\"")
	#print("Type is \"" + type + "\"")
	
	m = re.search(r"\nCookie: (?P<cookie>[\d]+)\r\n",request)
	if(m is not None):
		if(m.group("cookie") is not None):
			cookie = m.group("cookie")
			
	if(cookie not in cookieDict):
		cookieDict[cookie] = time.time()
			
	if(type == "GET"):
		if(resource == "/"):
			sendIndex(client,address)
		else:
			print("resource not found")
			
	elif(type == "POST"):
		message = request.split("\r\n\r\n")[1]
		if(message != ""):
			print(message)
			handlePost(client,address,message)
		sendPosts(client,address,cookie)
	
	client.close()
	
	
def sendIndex(client,address):
	print("SEND INDEX")
	client.sendall(formatHTTP(indexHTML_bytes))
	print("sent")
	
	
def handlePost(client,address,message):
	global postArr
	postSemaphore.acquire()
	postArr.append([time.time(),message])
	postSemaphore.release()
	
def sendPosts(client,address,cookie):
	global postArr
	message = ""
	if(cookie in cookieDict):
		ct = cookieDict[cookie]
	else:
		print("COOKIE NOT FOUND?")
		ct = time.time()
		
	popCount = 0
	tCutoff = time.time() - 5
	
	postSemaphore.acquire()
	for p in postArr:
		if(p[0] < tCutoff):
			popCount += 1
		elif(ct < p[0]):
			message += p[1]
			message += "\n"
	if(popCount > 0):
		postArr = postArr[popCount:]
		print(popCount,"posts decayed",len(postArr),"posts still saved")
	postSemaphore.release()
	
	cookieDict[cookie] = time.time()
	client.sendall(formatHTTP(message.encode("utf-8"),skipCookie=True))
	
	
		
	
	
def main():
	server1 = threading.Thread(target=startServer,args=["0.0.0.0",80],daemon=True)
	server1.start()
	input("Press enter at any time to stop\n")
	
	
if __name__ == "__main__":
	main()