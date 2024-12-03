import socket #Import socket library for network communication
from pymongo import MongoClient
from datetime import datetime, timedelta

def connect_to_database():
    client = MongoClient("mongodb+srv://bryan:1234@cluster0.krhmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") #mongo connection
    db = client["test"] #database name
    return db

def get_average_moisture(db):
    

def get_average_water_consumption(db):
    

def get_highest_electricity_consumer(db):
    

def process_query(query, db):
    if query == "What is the average moisture inside my kitchen fridge in the past three hours?":
        return get_average_moisture(db) #calculations returned for query
    elif query == "What is the average water consumption per cycle in my smart dishwasher?":
        return get_average_water_consumption(db) #calculations returned for query
    elif query == "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?":
        return get_highest_electricity_consumer(db) #calculations returned for query
    else:
        return "Error: Invalid query." #failsafe/debug
    
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a TCP/IP socket
    
    server_ip = input("Enter the server IP address: ") #Prompt for the server IP address
    server_port = int(input("Enter the port number to bind the server to: ")) #Prompt for the server port number
    
    server_socket.bind((server_ip, server_port)) #Bind the socket to the IP address and port entered by user
    
    server_socket.listen(1) #Listen for 1 incoming connection
    print(f"Server listening on {server_ip}:{server_port}") #Output a message indicating the server is ready
    
    db = connect_to_database()

    while True: #Infinite loop to handle multiple clients
        connection, client_address = server_socket.accept() #Accept an incoming client connection
        try:
            print(f"Connected to {client_address}") #Print the address of the connected client
            while True: #Handle communication with this client in a loop (to handle multiple messages)
                data = connection.recv(1024) #Receive up to 1024 bytes of data from the client
                if data: #If we get data, do the following:
                    query = data.decode('utf-8') #decode received data
                    print(f"Server received: {query}") #Print the received data
                    response = process_query(query, db) #process the query
                    connection.sendall(response.encode('utf-8')) #Send the processed data back to the client
                else:
                    break #If no data is received, break the loop
        finally:
            connection.close() #Close the client connection when done

if __name__ == "__main__":
    start_server() #Start the server
