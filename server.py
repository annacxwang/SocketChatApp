import socket
import select
import sys 
from _thread import *

PORT = 1234
IP = "localhost"
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind((IP, PORT))
serverSocket.listen(5)

clientList = []
clients = {}

def generateHeaders(response_code):
    """
    Generate HTTP response headers.
    Parameters:
        - response_code: HTTP response code to add to the header. 200 and 404 supported
    Returns:
        A formatted HTTP header for the given response_code
    """
    header = ''
    if response_code == 200:
        header += "HTTP/1.1 200 OK\r\n"
        header += "Content-Type: text/html; charset=utf-8\r\n"
        header += "\r\n"
    elif response_code == 404:
        header += "HTTP/1.1 404 Not Found\r\n\r\n"
    return header

def clientThread(conn, addr):
    PACKET_SIZE = 2048
    while True: 
        data = conn.recv(PACKET_SIZE).decode()
        if not data: break
   #     print("whole thing:",data)
        request_method = data.split(' ')[0]
        print("Method: {m}".format(m=request_method))
        print("Request Body: {b}".format(b=data))

        if request_method == "POST":
            action = data.split(' ')[1]
            if action == "/":
                temp = data.split('\n')
                data_body = temp[-1].strip()
                username = data_body.split("=")[1]
                clients[username] = conn
                file_requested = "/chat.html"
            else:
                #TO-DO:update message log

        elif request_method == "GET" or request_method == "HEAD":
            file_requested = data.split(' ')[1]
            file_requested =  file_requested.split('?')[0]

            if file_requested == "/":
                file_requested = "/index.html"
            elif file_requested == "/listOfUsers":
                #print("TRYING TO GET::::",file_requested)
                response = ""
                for username in clients.keys():
                    if clients[username]!=conn:
                        response+=("%%%"+username)
                conn.sendall(response.encode())
                conn.close()
                break

        else:
            print("Unknown HTTP request method: {method}".format(method=request_method))


        filepath_to_serve = 'html' + file_requested
        print("Serving web page [{fp}]".format(fp=filepath_to_serve))

        # Load and Serve files content
        try:
            f = open(filepath_to_serve, 'r')
            if request_method == "GET": # Read only for GET
                response_data = f.read()
            f.close()
            response_header = generateHeaders(200)
        except Exception as e:
            print("File not found. Serving 404 page.")
            response_header = generateHeaders(404)

            if request_method == "GET": # Temporary 404 Response Page
                response_data = "<html><body><center><h1>Error 404: File not found</h1></center><p>Head back to <a href='/'>dry land</a>.</p></body></html>"

        response = response_header
        if request_method == "GET":
            response += response_data
        print(response)

        conn.sendall(response.encode())
        conn.close()
        break

def broadcast(message, connection): 
    for clients in clientList: 
        if clients!=connection: 
            try: 
                clients.send(message) 
            except: 
                clients.close() 
  
                # if the link is broken, we remove the client 
                remove(clients) 
  
def remove(connection): 
    if connection in clientList: 
        clientList.remove(connection) 
  
while True: 
  
    """Accepts a connection request and stores two parameters,  
    conn which is a socket object for that user, and addr  
    which contains the IP address of the client that just  
    connected"""
    conn, addr = serverSocket.accept() 
   
    clientList.append(conn) 

    print (addr[0] + " connected")
  
    start_new_thread(clientThread,(conn,addr))     
  
conn.close() 
serverSocket.close()
