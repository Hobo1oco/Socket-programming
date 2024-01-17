import socket
import sys
import os


def serverMain():
    port = int(input("Please entre the port number:\n")) #Get port number
    if port < 1024 or port > 64000:
        print("Sorry, Port number should between 1024 and 64000.\n")
        sys.exit()
    else:
        server = createSocket(port)
    server.settimeout(120) #set a very long time out just in case i have time to test
    server = listenClient(server)
    infiniteLoop(server, port) 
    
    
def createSocket(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('127.0.0.1', port)) #set IP address 127.0.0.1
    except:
        print("Sorry, Binding Failed.\n")
        sys.exit()
    return server

def listenClient(server): #Listen from Client
    try:
        server.listen()
        print("-----Please wait for Client command-----")
    except:
        print("Sorry, Server listen Failed.\n")
        server.close()
        sys.exit()
    return server

def infiniteLoop(server, port):
    while True:
        client, address = server.accept()
        pri = ("| Connection Succeed with {}, Port Number is {} |".format(address, port))
        useless = (len(pri) * '-')
        print(useless)
        print(pri)
        print(useless)      #just want make my terminal looks better.
        client.settimeout(60)
        messRequest(client)

def messRequest(client):#get messageRequest from client
    try:
        message = client.recv(255)
    except:
        print("Sorry, Receive Failed.\n")
        client.close()
    checkRequest(client, message)
    
def checkRequest(client, message):#check everything is good or not
    request = bytearray(message)
    if (((request[0] << 8 )| (request[1])) != 0xAE73):
        print("Sorry, MagicNo must equal 0xAE73.")
        client.close()
    elif request[2] != 1 and request[2] != 2:
        print("Sorry, ID must be 1 or 2.{}\n".format(request[2]))
        client.close()
    elif request[3] < 1:
        print("Sorry, Name can not be empty\n")
        client.close()   
    else:
        fileOpen(client, request)

def fileOpen(client, request):    #i think my code is go wrong from here, but i can't find it
    message = request[7:].decode()  #basicly check user want read or create
    user = message[:request[3]]
    if request[2] == 2:
        if request[2] == 2 and request[4] < 1:
            print("Sorry, Receiver Name can not be empty.\n")
            client.close()        
        elif request[2] == 2 and ((request[5] << 8 )| (request[6])) < 1:
            print("Sorry, Message can not be empty.\n")
            client.close()  
        #if user want create, my thought is build a new txt for user
        message = request[7:].decode()
        receiver = message[request[3]:(request[3]+request[4])]
        text = message[request[3]+request[4]:]
        createTxt(str(user), str(receiver), str(text))
    if request[2] == 1:  #for user want to read message
        if request[2] == 1 and request[4] > 1:
            print("Sorry, Reading request do not need Receiver Name.\n")
            client.close()         
        elif request[2] == 1 and ((request[5] << 8 )| (request[6])) > 1:
            print("Sorry, Reading request do not need entre Message.\n")
            client.close()
        
        readTxt(client, user)
        
def createTxt(user, receiver, text):      #which server can create a txt for message      
    b = os.getcwd()[0:] + "\\"      #find where server.py are
    num = 1
    name = b + user + ','+ receiver + str(num) + '.txt'     #give the name and path of message, the txt file title combine with sender name and receiver name, easy to find later
    while os.path.exists(name): #if there already have a message from same user and receiver
        num += 1                #then make sure new message would not replace the old one by changing name
        name = b + user + ',' + receiver + str(num) + '.txt'
    file = open(name,'w')
    file.write(text)
    print("Message have saved at {} in server".format(name))
    file.close() #basicly create file finished
    

def readTxt(client, user):      #use to get a list that how many message are send to user
    b = os.getcwd()[0:] + "\\"  #find where server put message
    num = 1
    list1 = []      #list use to append message that below to user 
    rece = str(user) + str(num)
    for filename in os.listdir(b): #list everything in server path
        if os.path.splitext(filename)[1] == '.txt':
            while (rece.lower() == (os.path.splitext(filename)[0]).split(',')[-1].lower()):# split by name to find user's message
                list1.append(filename)
                num += 1
                rece = str(user) + str(num)            
    openFile(client, list1, user)

def openFile(client, dic, user): #now we have the files that user is the receiver
    b = os.getcwd()[0:] + "\\"
    message = ''
    sender = ''
    total_byte = 0
    numtimes = len(dic) #doesn't really know what is numitems, i guess should be how many message left behind
    more = 0
    if len(dic) > 0:
        for mail in dic:
            sender = (os.path.splitext(mail)[0].split(','))[0] #we don't know sender at first, so i use this to find sender
            message = ''
            name = b + mail
            file = open(name)
            lines = file.readlines()
            for line in lines:
                message += line #make all the message we have in txt together but can not more than 255
            while len(message) > 255:
                more = 1
                mess255 = message[:255]
                message = message[255:]
                #build response message
                feedback = messageResponse(client, 3, numtimes, more, sender, mess255)
                total_byte += len(feedback) #please ignore this one here, i was tring to show some coll things use this
                more = 0
                client.send(feedback)
            feedback = messageResponse(client, 3, numtimes, more, sender, message)
            total_byte += len(feedback)
            client.send(feedback)
            numtimes -= 1
            file.close()
        print("Totally {} bytes send succeed.".format(total_byte))
    else:
        print("Sorry, No message for {} in server.".format(user))
        feedback = messageResponse(client, 3, 0, 0, sender, message)
        client.send(feedback)
    client.close()
    delMail(dic) #the file once we send back to client, better to remove old one, in case next time cause some chaos

def delMail(dic):
    for mail in dic:
        if os.path.exists(mail):
            os.remove(mail)    



def messageResponse(client, ID, numitems, moremsgs, sender, message):
    request = bytearray([
        (0xAE73 & 0xFF00) >> 8,
        (0xAE73 & 0xFF),
        (ID),
        (numitems),
        (moremsgs),
        (len(sender.encode('utf-8'))),
        (len(message.encode('utf-8')) & 0xFF00)>>8,
        (len(message.encode('utf-8')) & 0xFF)])
    for byte in sender.encode():
        request.append(byte)
    for byte in message.encode():
        request.append(byte)
    return request




if __name__ == '__main__':
    serverMain()
