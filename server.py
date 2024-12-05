import socket
from pymongo import MongoClient
from datetime import datetime

# Define a binary tree node for managing IoT metadata
class TreeNode:
    def __init__(self, key, data):
        self.key = key  # the device ID
        self.data = data  # Metadata
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, key, data):
        if self.root is None:
            self.root = TreeNode(key, data)
        else:
            self._insert(self.root, key, data)

    def _insert(self, node, key, data):
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key, data)
            else:
                self._insert(node.left, key, data)
        elif key > node.key:
            if node.right is None:
                node.right = TreeNode(key, data)
            else:
                self._insert(node.right, key, data)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right)

# fetch and process data from MongoDB
def fetch_data_from_db(query, metadata_tree):
    try:
        client = MongoClient(
            "mongodb+srv://AnthonyTorres1327:Zenny1327@cluster0.mo9sc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
            tlsAllowInvalidCertificates=True
        )
        db = client["test"]
        collection = db["Data_virtual"]

        # print(f"Processing query: {query}")

        # Handle RH (moisture) queries
        if "moisture" in query.lower() or "humidity" in query.lower():
            # print("Debug: Entered moisture query branch.")
            query_filter = {"payload.parent_asset_uid": "u02-m89-3n6-27i"}
            matching_docs = collection.find(query_filter)

            rh_values = []
            for record in matching_docs:
                payload = record.get("payload", {})
                moisture = payload.get("Moisture Meter - Moisture meter")
                if moisture is not None:
                    try:
                        rh_value = float(moisture) * 0.75
                        rh_values.append(rh_value)
                    except ValueError:
                        # print(f"Invalid moisture value: {moisture}")
                        pass

            if not rh_values:
                return "No RH data available for the query."

            avg_rh = sum(rh_values) / len(rh_values)
            return f"Average RH% in the past three hours: {avg_rh:.2f}%"

        # Handle water consumption queries
        elif "water consumption" in query.lower() or ("dishwasher" in query.lower() and "water" in query.lower()):
            # print("Entered water consumption query branch.")
            query_filter = {"payload.parent_asset_uid": "3974758e-7175-4519-8a68-be1f7ff45c63"}
            matching_docs = collection.find(query_filter)

            # print("Retrieved water consumption documents:")
            water_usage_values = []
            for record in matching_docs:
                payload = record.get("payload", {})
                # print(f"Payload for water query: {payload}")
                for key, value in payload.items():
                    if "sensor" in key.lower() or "water" in key.lower(): 
                        try:
                            water_value = float(value)
                            water_usage_values.append(water_value)
                            # print(f"Added {value} to water usage list")
                        except ValueError:
                            # print(f"Invalid water sensor value: {value}")
                            pass

            if not water_usage_values:
                return "No water consumption data available for the query."

            avg_water_usage = sum(water_usage_values) / len(water_usage_values)
            return f"Average water consumption per cycle: {avg_water_usage:.2f} gallons"

        # Handle electricity consumption queries
        elif "electricity consumption" in query.lower() or ("electricity" in query.lower() and "consumed" in query.lower()):
            # print("Entered electricity consumption query branch.")
            device_ids = [
                "u02-m89-3n6-27i",  # SFridge 1
                "842fc7b3-851e-4389-abf4-d5a6180444f1",  # SFridge 2
                "3974758e-7175-4519-8a68-be1f7ff45c63"  # Dishwasher
            ]

            electricity_usage = {}
            standard_voltage = 120 
            time_hours = 1  # Assuming a 1-hour time period

            for device_id in device_ids:
                query_filter = {"payload.parent_asset_uid": device_id}
                matching_docs = collection.find(query_filter)

                # print(f"Retrieved electricity consumption documents for device {device_id}:")
                total_consumption = 0
                for record in matching_docs:
                    payload = record.get("payload", {})
                    # print(f"Payload for device {device_id}: {payload}")
                    for key, value in payload.items():
                        if "acs712" in key.lower() or "ammeter" in key.lower(): 
                            try:
                                current_amperes = float(value)
                                power_kwh = (current_amperes * standard_voltage * time_hours) / 1000  # Convert to kWh
                                total_consumption += power_kwh
                                # print(f"Added {power_kwh:.2f} kWh to total for {device_id}")
                            except ValueError:
                                # print(f"Invalid electricity sensor value: {value}")
                                pass

                electricity_usage[device_id] = total_consumption

            if not electricity_usage:
                return "No electricity consumption data available for the query."

            max_consumption_device = max(electricity_usage, key=electricity_usage.get)
            max_consumption_value = electricity_usage[max_consumption_device]
            return f"Device {max_consumption_device} consumed the most electricity: {max_consumption_value:.2f} kWh"

        # Default response for unknown queries
        return "No data available for the query."

    except Exception as e:
        # print(f"Error during query processing: {e}")
        return "An error occurred while processing the query."

# Server setup
def start_server():
    host = "0.0.0.0"
    port = 5000

    print("Server Running -- waiting for connection.")
    MyTcpServer_socket = socket.socket()
    MyTcpServer_socket.bind((host, port))
    MyTcpServer_socket.listen(2)

    # Initialize metadata tree
    metadata_tree = BinaryTree()
    metadata_tree.insert("u02-m89-3n6-27i", {
        "device_id": "u02-m89-3n6-27i",
        "data_source": "moisture",
        "unit": "RH%",
        "timezone": "PST"
    })
    metadata_tree.insert("3974758e-7175-4519-8a68-be1f7ff45c63", {
        "device_id": "3974758e-7175-4519-8a68-be1f7ff45c63",
        "data_source": "water_usage",
        "unit": "gallons",
        "timezone": "PST"
    })
    metadata_tree.insert("842fc7b3-851e-4389-abf4-d5a6180444f1", {
        "device_id": "842fc7b3-851e-4389-abf4-d5a6180444f1",
        "data_source": "electricity",
        "unit": "kWh",
        "timezone": "PST"
    })

    conn, address = MyTcpServer_socket.accept()
    print(f"Connection from: {address}")

    while True:
        try:
            data = conn. recv(1024).decode()
            if not data:
                break

            result = fetch_data_from_db(data, metadata_tree)
            conn.send(result.encode())
        except Exception as e:
            print(f"Error during communication: {e}")


    conn.close()

    print("Connection closed.")

# Start server
if __name__ == "__main__":
    start_server()