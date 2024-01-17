import socket
import sys
import os
def clientMain():
    message = None
    print("The IP address defaults to this 127.0.0.1")
    address = input("Please entre the IP or address:\n")
    portnum = getPortnumber()
    ip = getAddress(address, portnum)
    user = getUsername()
    read_or_create = ReadorCreate()
    if read_or_create == 2:
        reciver = getReciver()
        message = getMessage()
    elif read_or_create == 1:
        reciver = ''
        message = ''
    client = createSocket()
    client.settimeout(30)
    result = messageRequest(client, read_or_create, user, reciver, message)
    connectToserver(client, address, portnum)   
    sendMessage(client, result)
    getResponse(client)


def sendMessage(client, message):
    try:
        client.send(message)
        print("Message Send Succeed.")
    except:
        print("Sorry, Message Send Failed.")
        sys.exit()

def connectToserver(client, addr, port):
    try:
        client.connect((addr, port))
        print("Connection Succeed.")
    except:
        print("Failed to connect to server")
        sys.exit()

def messageRequest(client, ID, name, receiver, message):
    request = bytearray([
        (0xAE73 & 0xFF00) >> 8,
        (0xAE73 & 0xFF),
        (ID),
        (len(name.encode('utf-8')) & 0xFF),
        (len(receiver.encode('utf-8'))),
        (len(message.encode('utf-8')) & 0xFF00)>>8,
        (len(message.encode('utf-8')) & 0xFF)])
    for byte in name.encode():
        request.append(byte)
    for byte in receiver.encode():
        request.append(byte)
    for byte in message.encode():
        request.append(byte)
    return request
    


def createSocket():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return client




def getSender():
    name = input("Please tell me who send you this message.\n")
    num = len(name)
    while num > 255 or num < 1: 
        name = input("Sorry, Name is too long or too short, Please try again.\n")
        num = len(name)
    return name

def getReciver():
    name = input("Please tell me reciver name.\n")
    num = len(name)
    while num > 255 or num < 1: 
        name = input("Sorry, Name is too long or too short, Please try again.\n")
        num = len(name)
    return name

def getMessage():
    message = input('Please text below:\n')
    num = len(message)
    while num > 65535 or num < 1: 
        message = input("Sorry, Message is too long or too short, Please try again.\n")
        num = len(message)
    return message
    
    
    
def getAddress(addr, port):
    
    try:
        new_addr = socket.getaddrinfo(addr, port)
        return sorted(new_addr)[0][-1][0]
    except:
        print("Sorry, Please entre valid address!\n")
        sys.exit()
    
        
def getPortnumber():
    port = input("Please entre the port number:\n")
    port = int(port)
    if port < 1024 or port > 64000:
        print("Sorry, Port number should between 1024 and 64000.\n")
        sys.exit()
    else:
        return port

def getUsername():
    name = input("Please tell me user name:\n")
    bname = name.encode("utf-8")
    if len(bname) < 1:
        print("Sorry, User name is too short!\n")
        sys.exit()
    elif len(bname) > 255:
        print("Sorry, User name is too long!\n")
        sys.exit()
    else:
        return name

def ReadorCreate():
    print("Entre 'Read'/'1' or 'Create'/'2' to continue. Tank you.")
    request = input("Read(1) or Create(2): ")
    if request.lower() == 'read' or request == '1':
        return 1
    elif request.lower() == 'create'or request == '2':
        return 2
    else:
        print("Sorry, Please entre a valid word.\n")
        sys.exit()
        
def getResponse(client):
    try:
        response = client.recv(255)
        client.settimeout(30)
    except:
        print("Sorry, Receive File Failed.")
        client.close()
        sys.exit()
    if (((response[0] << 8 )| (response[1])) != 0xAE73):
        print("Sorry, MagicNo must equal 0xAE73.")
        client.close()
        sys.exit()
    elif response[2] != 3:
        print("Sorry, ID must equal 3.")
        client.close()
        sys.exit()
    elif (response[4] != 0 and response[4] != 1):
        print("Sorry, Moremsgs must be 0 or 1.")
        client.close()
        sys.exit()
    elif (response[3] == 0):
        print("Sorry, There is no message for you.")
        client.close()
        sys.exit()
    else:
        readMessage(client, response)

        
def readMessage(client, response):
    client.settimeout(30)
    sender = (response[8:][:response[5]]).decode('utf-8')
    message = response[7:][response[5]+1:]
    result = message.decode('utf-8')
    txt(sender, result)


def txt(sender, text):            
    b = os.getcwd()[0:] + "\\"
    num = 1
    name = b + 'From' + ' '+ sender + str(num) + '.txt'
    while os.path.exists(name):
        num += 1
        name = b + 'From' + ' ' + sender + str(num) + '.txt'
    file = open(name,'w')
    file.write(text)
    file.close()
    print("The message from {} has saved at {}.".format(sender, name))    
    
if __name__ == '__main__':
    clientMain()