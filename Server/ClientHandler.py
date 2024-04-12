import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import pickle

from Models.User import User

class ClientHandler(threading.Thread):
    clienthandler_count = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        self.socket_to_client = socketclient
        self.io_stream_client = self.socket_to_client.makefile(mode='rw')
        self.messages_queue = messages_queue
        self.id = ClientHandler.clienthandler_count
        ClientHandler.clienthandler_count += 1

    def run(self):
        self.__print_message_gui_server("Started & waiting...")
        command = self.io_stream_client.readline().rstrip('\n')
        while command != "CLOSE":
            if command == "LOGIN":
                self.__handle_login()

            command = self.io_stream_client.readline().rstrip('\n')

        self.__print_message_gui_server("Connection with client closed...")
        self.io_stream_client.close()
        self.socket_to_client.close()
        

    def __handle_login(self):
        username = self.io_stream_client.readline().rstrip('\n')
        password = self.io_stream_client.readline().rstrip('\n')
        is_valid = self.__check_credentials(User(username, password))
        message = "Login successful\n" if is_valid else "Login failed\n"
        self.io_stream_client.write(message)
        self.io_stream_client.flush()
        self.__print_message_gui_server(message)
    
    def __check_credentials(self, input_user: User):
        my_reader_obj = open("./Data/users.txt", mode='rb')
        while True:
            try:
                stored_user = pickle.load(my_reader_obj)
                if stored_user == input_user:
                    my_reader_obj.close()
                    return True
            except EOFError:
                break
    
    def __print_message_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")