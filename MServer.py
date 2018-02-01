#!/bin/python
import select, signal, socket, sys
from random import randint

DEFAULT_PORT=10081

def generateMulticastGroupPort():
  return randint(10000,11000)

def generateMulticastGroupIP():
  return str(randint(224,239)) + '.' + str(randint(0,255)) + '.' + str(randint(0,255)) + '.' + str(randint(0,255))

def getServerSocket(port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((socket.gethostname(), port))
  print('Socket bound to host: ' + socket.gethostname() + ' on port: ' + str(port))
  s.listen(5)
  return s

#Send ip/port to all connected (keepalive response)
def sendMulticastInfo(s,multicastGroupPort,multicastGroupIP):
  try:
    s.sendall(multicastGroupIP + '|' + str(multicastGroupPort))
  except socket.error, e:
    pass

def printConnected(connected):
  if len(connected) > 0:
    print('Clients connected:')
    for value in connected:
      print(value)
  else:
    print('No client connected')

def startServer(port):
  s=getServerSocket(port)
  multicastGroupPort=generateMulticastGroupPort()
  multicastGroupIP=generateMulticastGroupIP()
  connected=[]
  signal_handler = lambda signum,frame: printConnected(connected)
  signal.signal(signal.SIGINT, signal_handler)
  
  connectionList=[s]
  while True:
    try:
      read_sockets,write_sockets,error_sockets = select.select(connectionList,[],[])
      for sock in read_sockets:
        #New connection
        if sock == s:
            
            sockfd, addr = s.accept()
            connectionList.append(sockfd)
            print "Client (%s, %s) is connected" % addr
            connected.append(str(sockfd.getpeername()))
            sendMulticastInfo(sockfd,multicastGroupPort,multicastGroupIP)
        
        else:
            
            try:
                
                data = sock.recv(1024) #doesn't block
                if data is None or data == '':
                  print "Client (%s, %s) has disconnected" % sock.getpeername()
                  connected.remove(str(sock.getpeername()))
                  connectionList.remove(sock)
                  sock.close()
            except:
                print "Client (%s, %s) is offline" % sock.getpeername()
                connected.remove(sock.getpeername())
                sock.close()
                connectionList.remove(sock)
                continue
    except:
      
      pass

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('User did not specify port#, using default port ' + str(DEFAULT_PORT))
    port=DEFAULT_PORT
  else:
    port=int(sys.argv[1])
  startServer(port)