import socket
import threading
import re
import time
import datetime
import random

names = open("names.txt","r").read().strip().split("\n")
indexHTML_bytes = open("index.html","r").read().encode("utf-8")
postSemaphore = threading.BoundedSemaphore(1)
postArr = []
cookieDict = {}

def randomUsername():
	return random.choice(names)
	
def randomColor():
	letters = list("9ABCDEF")
	color = []
	for i in range(6):
		color += [random.choice(letters)]
		
	a,b = random.choice([[0,1],[2,3],[4,5]])
	for i in range(a,b):
		color[i] = random.choice(list("F"))
	
	return "`" + "".join(color)

def generateCookie():
	i = random.randint(1,2000000000000000)
	t = time.time()
	cookieDict[str(i)] = [t,randomColor(),randomUsername()]
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
		cookieDict[cookie] = [time.time(),randomColor(),randomUsername()]
			
	if(type == "GET"):
		if(resource == "/"):
			sendIndex(client,address)
		else:
			print("resource not found")
			
	elif(type == "POST"):
		message = request.split("\r\n\r\n")[1]
		if(message != ""):
			print(message)
			handlePost(client,address,message,cookie)
		sendPosts(client,address,cookie)
	
	client.close()
	
	
def sendIndex(client,address):
	print("SEND INDEX")
	client.sendall(formatHTTP(indexHTML_bytes))
	print("sent")
	
	
def handlePost(client,address,message,cookie):
	global postArr
	message = message.replace("`","?")	
	postSemaphore.acquire()
	username = "???"
	color = "`FFFFFF"
	if(cookie in cookieDict):
		username = cookieDict[cookie][2]
		color = cookieDict[cookie][1]
	postArr.append([time.time(),"[" + datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S') + " " + username + "] " + message,color])
	postSemaphore.release()
		
def sendPosts(client,address,cookie):
	global postArr
	message = ""
	color = "`FFFFFF"
	if(cookie in cookieDict):
		ct = cookieDict[cookie][0]
		cookieDict[cookie][0] = time.time()
	else:
		print("COOKIE NOT FOUND?")
		ct = time.time()
		cookieDict[cookie] = [ct,randomColor(),randomUsername()]
		
	popCount = 0
	tCutoff = time.time() - 5
	
	postSemaphore.acquire()
	for p in postArr:
		if(p[0] < tCutoff):
			popCount += 1
		elif(ct < p[0]):
			message += p[2] + "; " + p[1]
	if(popCount > 0):
		postArr = postArr[popCount:]
		print(popCount,"posts decayed",len(postArr),"posts still saved")
	postSemaphore.release()
	
	
	client.sendall(formatHTTP(message.encode("utf-8"),skipCookie=True))
	
	
		
	
	
def main():
	server1 = threading.Thread(target=startServer,args=["0.0.0.0",80],daemon=True)
	server1.start()
	input("Press enter at any time to stop\n")
	
	
if __name__ == "__main__":
	main()