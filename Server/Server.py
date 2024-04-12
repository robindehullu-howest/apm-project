import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import socket
import pickle
import threading

from ClientHandler import ClientHandler

logging.basicConfig(level=logging.INFO)

class Server(threading.Thread):
    def __init__(self, host, port, message_queue):
        threading.Thread.__init__(self, name="Thread-Server")
        self.__is_connected = False
        self.host = host
        self.port = port
        self.message_queue = message_queue
        self.serversocket = None

    @property
    def is_connected(self):
        return self.__is_connected
    
    def init_server(self):
        # Create a socket object
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.__is_connected = True
        self.print_message_gui_server("Server started")
        logging.info("Server started")

    def close_server_socket(self):
        if self.serversocket is not None:
            self.serversocket.close()

    def run(self):
        try:
            while True:
                self.print_message_gui_server("Waiting for a client...")

                # Establish a connection
                socket_to_client, addr = self.serversocket.accept()
                self.print_message_gui_server(f"Got a connection from {addr}")

                clh = ClientHandler(socket_to_client, self.message_queue)
                clh.start()
                self.print_message_gui_server(f"Current Thread count: {threading.active_count()}.")
        except Exception as ex:
            self.print_message_gui_server("Server socket closed")

    def print_message_gui_server(self, message):
        self.message_queue.put(f"Server:> {message}")
