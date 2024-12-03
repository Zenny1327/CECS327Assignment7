import socket #Import socket library for network communication

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a TCP/IP socket
    
    server_ip = input("Enter the server IP address: ") #Prompt for the server IP address
    server_port = int(input("Enter the server port number: ")) #Prompt for the server port number
    
    valid_queries = [
        "What is the average moisture inside my kitchen fridge in the past three hours?",
        "What is the average water consumption per cycle in my smart dishwasher?",
        "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    ] #queries that are valid

    try:
        client_socket.connect((server_ip, server_port)) #Attempt to connect to the server (using try)
        print(f"Successfully connected to server on {server_ip}:{server_port}") #Confirm the connection to the server
        
        while True: #Infinite loop to handle multiple messages
            print("\nAvailable Queries:")
            print("What is the average moisture inside my kitchen fridge in the past three hours?")
            print("What is the average water consumption per cycle in my smart dishwasher?")
            print("Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
            message = input("Enter your query (or type 'exit' to quit): ")
            if message.lower() == 'exit': #If the user types 'exit', break the loop. Client ends
                break
            elif message in valid_queries: #send valid queries to TCP server
                client_socket.sendall(message.encode('utf-8'))
                response = client_socket.recv(1024)
                print(f"Server response: {response.decode('utf-8')}")
            else:
                print(f"Sorry, this query cannot be processed. Please try one of the following: {valid_queries}.") #let them know the query couldn't be processed

    except ConnectionError as e: #Handle any connection-related errors
        print(f"Error: Could not connect to server. Issue: {e}") #Print an error message if the connection fails
    
    finally:
        client_socket.close() #Close the socket connection when done

if __name__ == "__main__":
    start_client() #Start the client
