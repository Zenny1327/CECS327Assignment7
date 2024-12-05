import socket

# valid queries
VALID_QUERIES = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]

def is_valid_query(query):
    """Check if the input query is valid."""
    return query in VALID_QUERIES

# Prompt user for IP address and port number
server_ip = input("Enter the server IP address: ")
port = input("Enter the server port number: ")

try:
    port = int(port)
    client_socket = socket.socket()  # Instantiate the socket

    # Connect to the server with the provided IP and port
    client_socket.connect((server_ip, port))
    print(f"Connected to server at {server_ip}:{port}")

    while True:
        # Prompt user for a query
        query = input("Enter your query (type 'stop' to cease communications) ->: ")

        # Exit the loop if the user types 'stop'
        if query.lower().strip() == 'stop':
            print("Closing connection...")
            break

        # Check if the query is valid
        if not is_valid_query(query):
            print("Sorry, this query cannot be processed. Please try one of the following:")
            for valid_query in VALID_QUERIES:
                print(f"- {valid_query}")
            continue

        # Send valid query to the server
        print(f"Sending query to server: {query}")
        client_socket.send(query.encode())

        # Receive and display response from the server
        try:
            client_socket.settimeout(100)  # Timeout to avoid indefinite waiting
            data = client_socket.recv(1024).decode()
            print(f"Received from server: {data}")
        except socket.timeout:
            print("No response from the server, connection timed out.")

except ValueError:
    # User input error checking
    print("Error: Port number must be an integer.")

except socket.error as e:
    print(f"Connection error: {e}")

finally:
    client_socket.close()  # Close the connection
    print("Client connection closed.")
