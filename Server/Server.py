import os
import sys
import logging
import socket
import threading

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ClientHandler import ClientHandler

logging.basicConfig(level=logging.INFO)

LOGGED_USERS_PATH = "./Data/logged_users.txt"

class Server(threading.Thread):
    def __init__(self, host, port, message_queue):
        threading.Thread.__init__(self, name="Thread-Server")
        self.host = host
        self.port = port
        self.message_queue = message_queue
        self.serversocket = None

        self.init_server()
        self.clear_logged_users()
    
    def init_server(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.print_message_gui_server("Server started")
        logging.info("Server started")

    def close_server_socket(self):
        try:
            self.serversocket.close()
            self.print_message_gui_server("Server socket closed")
            self.clear_logged_users()
        except Exception as ex:
            logging.error("Socket is already closed.")

    def clear_logged_users(self):
        # Clear the logged users file
        with open(LOGGED_USERS_PATH, "w") as file:
            file.write("")

    def run(self):
        try:
            while self.serversocket is not None:
                self.print_message_gui_server("Waiting for a client...")

                # Establish a connection
                socket_to_client, addr = self.serversocket.accept()
                self.print_message_gui_server(f"Got a connection from {addr}")

                clh = ClientHandler(socket_to_client, self.message_queue)
                clh.start()
                self.print_message_gui_server(f"Current Thread count: {threading.active_count()}.")
            
            active_client_handlers = self.get_active_client_handlers()
            for client_handler in active_client_handlers:
                client_handler.close_socket = True

        except Exception as ex:
            self.print_message_gui_server(ex)
            logging.error(f"Error in Server: {ex}")

    def broadcast_message(self, message):
        active_client_handlers = self.get_active_client_handlers()
        for client_handler in active_client_handlers:
            client_handler.send_messages("BROADCAST", [message])

    def print_message_gui_server(self, message):
        self.message_queue.put(f"Server:> {message}")

    def get_active_client_handlers(self):
        return [t for t in threading.enumerate() if isinstance(t, ClientHandler)]
