import socket
import random
import time

doge_message = """
                   ▄              ▄
                  ▌▒█           ▄▀▒▌
                  ▌▒▒█        ▄▀▒▒▒▐
                 ▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐
               ▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐
             ▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌
            ▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒▌
            ▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐
           ▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀▄▌
           ▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▌
          ▌▒▀▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒▒▐
          ▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒▒▒▌
          ▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒▒▐
           ▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒▒▌
           ▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒▐
            ▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒▌
              ▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀
                ▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀
                   ▒▒▒▒▒▒▒▒▒▒"""

def getMessageBytes(cookie,message):
	m = """POST / HTTP/1.1\r	Host: 127.0.0.1\r	Connection: keep-alive\r	Content-Length: 0\r	Origin: http://127.0.0.1\r	User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/53\r	Chrome/65.0.3325.162 Safari/537.36\r	Content-type: application/x-www-form-urlencoded\r	Accept: */*\r	DNT: 1\r	Referer: http://127.0.0.1/\r	Accept-Encoding: gzip, deflate, br\r	Accept-Language: en-US,en;q=0.9\r
	Cookie: """ + str(cookie) + "\r\n\r\n" + message + "\r\n\r\n"
	return m.encode("utf-8")

for i in range(1):
	s = socket.socket()
	s.connect(("127.0.0.1",80))
	cookie = random.randint(1,200000000)
	m = ("<br>").join((doge_message.replace(" ",".")).split("\n"))
	s.send(getMessageBytes(cookie,"<br>" + m))
	#print(s.recv(10000000))
	s.close()
	time.sleep(.001)
