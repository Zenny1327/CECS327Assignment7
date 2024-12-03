import socket #Import socket library for network communication
from pymongo import MongoClient
from datetime import datetime, timedelta

device_name_map = {
    "Arduino Pro Mini - Smart Refrigerator": "Smart Refrigerator",
    "board 1 fb71d801-aef5-4fdd-ae9b-fd69f683a28c": "Smart Refrigerator 2",
    "board 1 155ca01a-f896-4ab5-b1cb-1043505d7dcc": "Smart Dishwasher"
} #dictionary for dataniz's inability to change device name

def convert_to_pst(utc_time):
    pst_time = utc_time - timedelta(hours=8) 
    return pst_time

def connect_to_database():
    client = MongoClient("mongodb+srv://bryan:1234@cluster0.krhmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") #mongo connection
    db = client["test"] #database name
    return db

def get_average_moisture(db):
    current_time = datetime.utcnow()
    three_hours_ago = current_time - timedelta(hours=3)

    current_pst = convert_to_pst(current_time)
    three_hours_ago_pst = convert_to_pst(three_hours_ago)

    #find the moisture data in the past 3 hours
    readings = db["DD1_virtual"].find({
        "payload.topic": "Connection",
        "payload.board_name": {"$regex": "Arduino Pro Mini - Smart Refrigerator", "$options": "i"}, #match any string that has that board name. case insensitive
        "payload.timestamp": {"$gte": three_hours_ago.timestamp()} #all documents that are greater than or equal to the value of the 3 hours ago timestamp (earlier the timestamp, older the document)
    })

    #extract moisture values
    moisture_values = [doc["payload"]["Moisture Meter"] for doc in readings] #extract moisture meter documents
    if moisture_values:
        avg_moisture = sum(moisture_values) / len(moisture_values) #calculate average. sum of all moisture values divided by how many there are
        return f"Average moisture inside the fridge, for the past 3 hours, from {three_hours_ago_pst} to {current_pst}: {avg_moisture:.2f}% RH" #relative humidity to the second decimal point
    else:
        return "No moisture data is available for the specified time range." #failsafe

def get_average_water_consumption(db):
    #find the water consumption data
    readings = db["DD1_virtual"].find({
        "payload.topic": "Connection",
        "payload.board_name": {"$regex": "board 1 155ca01a-f896-4ab5-b1cb-1043505d7dcc", "$options": "i"} #match any string that has that board name. case insensitive
    })

    #extract water consumption values
    water_values = [doc["payload"]["Water Consumption Sensor"] for doc in readings] #extract water consumption sensor documents
    if water_values:
        avg_water = sum(water_values) / len(water_values) #calculate average. sum of all water consumption values divided by how many there are
        return f"Average water consumption per cycle: {avg_water:.2f} gallons" #gallons to the second decimal point
    else:
        return "No water consumption data is available." #failsafe   

def get_highest_electricity_consumer(db):
    devices = ["Arduino Pro Mini - Smart Refrigerator", "board 1 fb71d801-aef5-4fdd-ae9b-fd69f683a28c", "board 1 155ca01a-f896-4ab5-b1cb-1043505d7dcc"] #board names
    consumption = {} #store electricity consumption for each device (dictionary so we can look it up and organize it by device)

    #extract ammeter values
    for device in devices: #iterate through devices
        readings = db["DD1_virtual"].find({
            "payload.topic": "Connection",
            "payload.board_name": {"$regex": device, "$options": "i"} #match any string that has that board name. case insensitive
        })
        consumption[device] = sum(doc["payload"]["Ammeter - Dishwasher"] for doc in readings) #sum of the ammeter values for this device

    if consumption:
        max_device = max(consumption, key=consumption.get) #looks at each device and finds the one with highest ammeter value
        #convert names back to something more readable
        for raw_name, proper_name in device_name_map.items():
            max_device = max_device.replace(raw_name,proper_name)
        return f"{max_device} consumed the most electricity with {consumption[max_device]:.2f} kWh." #kWh to the second decimal point
    else:
        return "No electricity consumption data available." #failsafe

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

                    #convert names back to something more readable
                    for raw_name, proper_name in device_name_map.items():
                        response = response.replace(raw_name,proper_name)

                    connection.sendall(response.encode('utf-8')) #Send the processed data back to the client
                else:
                    break #If no data is received, break the loop
        finally:
            connection.close() #Close the client connection when done

if __name__ == "__main__":
    start_server() #Start the server
