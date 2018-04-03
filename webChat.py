import socket
import threading
import re
import time
import datetime
import random
import os
import ssl

names = open("names.txt","r").read().strip().split("\n")
indexHTML_bytes = open("index.html","r").read().encode("utf-8")
postSemaphore = threading.BoundedSemaphore(1)
cookieSemaphore = threading.BoundedSemaphore(1)
lastActiveSempaphore = threading.BoundedSemaphore(1)
postArr = []
cookieDict = {}
cookieFileName = "cookieDict.txt"
lastTimeCookiesSaved = time.time()
lastActiveUsers = set()

def saveCookieDict():
	with open(cookieFileName,"w") as f:
		cookieSemaphore.acquire()
		for k,v in cookieDict.items():
			#print("saving",k,v)
			f.write(k + "\t" + v[1] + "\t" + v[2] + "\t" + v[3] + "\n")
		cookieSemaphore.release()
	print("Saved cookies to dict")
		
def loadCookieDict():
	if(os.path.isfile(cookieFileName)):
		with open(cookieFileName,"r") as f:
			cookies = f.readlines()
		
		cookieSemaphore.acquire()
		for c in cookies:
			cookie, color, username, address = c.strip().split("\t")
			print("Loaded cookie",cookie,"for",username,"last @",address)
			cookieDict[cookie] = [0,color,username,address]
		cookieSemaphore.release()
	
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
	letters = list("abcdefghikllmnopqrstuvwxyz0123456789")
	cookie = ""
	cookieSemaphore.acquire()
	while True:
		cookie = ""
		for i in range(8):
			cookie += random.choice(letters)
		if(cookie not in cookieDict):
			break
	t = time.time()
	
	
	cookieDict[cookie] = [t,randomColor(),randomUsername(),"?"]
	cookieSemaphore.release()
	
	print("cookie",cookie,"added at time",t)
	return cookie

def formatHTTP(response,cookie=None,skipCookie=False):
	#httpOK = "HTTP/1.1 200 OK\r\nContent-Length:"
	httpOK = "HTTP/1.1 200 OK\r\n"
	if(skipCookie is False):
		httpOK += "Set-Cookie:" + cookie + "; Expires = Tue, 09 Jan 2024 08:00:00 GMT\r\n"
	httpOK += "\r\n"
	#l = len(response)
	header = (httpOK).encode("utf-8")
	#print("SENDING:::\n" + str(header) + str(response) + "\n")
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
	cookie = None
	skipCookie = False
	if(m is not None):
		if(m.group("type") is not None):
			type = m.group("type")
		if(m.group("resource") is not None):
			resource = m.group("resource")
		
	#print("Resource is \"" +resource+"\"")
	#print("Type is \"" + type + "\"")
	
	m = re.search(r"\nCookie: (?P<cookie>[a-z0-9]+)\r\n",request)
	if(m is not None):
		if(m.group("cookie") is not None):
			cookie = m.group("cookie")
			
	if(cookie not in cookieDict):
		cookie = generateCookie()
	else:
		skipCookie = True
	
	cookieSemaphore.acquire()
	cookieDict[cookie][3] = address[0]
	cookieSemaphore.release()
		
	if(type == "GET"):
		if(resource == "/"):
			sendIndex(client,address,cookie,skipCookie)
		else:
			pass
			#print("resource not found")
			
	elif(type == "POST"):
		message = request.split("\r\n\r\n")[1]
		if(message != ""):
			#print(message)
			handlePost(client,address,message,cookie)
		sendPosts(client,address,cookie,skipCookie)
	
	client.close()
	
	
def sendIndex(client,address,cookie,skipCookie):
	client.sendall(formatHTTP(indexHTML_bytes,cookie=cookie, skipCookie=skipCookie))

def serverStatusDaemon():
	while True:
		time.sleep(2)
		getActiveUsers()
	
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
	print(postArr[-1][1])
	postSemaphore.release()
	
def handleServerPost(message):
	global postArr
	color = "`7FB3D5"
	postSemaphore.acquire()
	postArr.append([time.time(),"[" + datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S') + " Server" + "] " + message,color])
	print(postArr[-1][1])
	postSemaphore.release()
		
def sendPosts(client,address,cookie,skipCookie):
	global postArr
	message = ""
	color = "`FFFFFF"
	if(cookie in cookieDict):
		ct = cookieDict[cookie][0]

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
	postSemaphore.release()
	
	cookieSemaphore.acquire()
	cookieDict[cookie][0] = time.time()
	cookieSemaphore.release()
	
	client.sendall(formatHTTP(message.encode("utf-8"), cookie=cookie, skipCookie=skipCookie))
	
	global lastTimeCookiesSaved
	if(lastTimeCookiesSaved + 300 < time.time()):
		lastTimeCookiesSaved = time.time()
		saveCookieDict()
		
	

def getActiveUsers():
	global lastActiveUsers
	
	activeCookies = []
	cookieSemaphore.acquire()
	for k,v in cookieDict.items():
		if(v[0] > time.time() - 5):
			activeCookies.append(k)
	cookieSemaphore.release()	
	
	#print("Active Users",activeCookies)
	lastActiveSempaphore.acquire()
	oldLastActiveUsers = lastActiveUsers
	lastActiveUsers = set(activeCookies)
	usersThatLeft = oldLastActiveUsers.difference(lastActiveUsers)
	usersThatJoined = lastActiveUsers.difference(oldLastActiveUsers)
	
	for u in usersThatLeft:
		handleServerPost(cookieDict[u][2] + " has left.")
	for u in usersThatJoined:
		handleServerPost(cookieDict[u][2] + " has joined.")
	lastActiveSempaphore.release()
	
def handleAdmin(command):
	if(command.startswith("send")):
		handleServerPost(command.split("send ",1)[1])
	
	elif(command == "w"):
		print("These users are here:")
		for k,v in cookieDict.items():
			if(v[0] > time.time() - 5):
				print("\t",v[2],v[3],k)
	
	elif(command.startswith("cn")):
		_,cookie,name = command.strip().split(" ")
		cookieSemaphore.acquire()
		cookieDict[cookie][2] = name
		cookieSemaphore.release()
		print("Changed",cookie,"'s name to",name)
		saveCookieDict()
	
	
def main():
	loadCookieDict()
	serverDispatch = threading.Thread(target=startServer,args=["0.0.0.0",80],daemon=True)
	serverDispatch.start()
	serverStatusThread = threading.Thread(target=serverStatusDaemon,daemon=True)
	serverStatusThread.start()
	try:
		while True:
			m = input()
			threading.Thread(target=handleAdmin,args=[m]).start()
	finally:
			saveCookieDict()
		
	
if __name__ == "__main__":
	main()