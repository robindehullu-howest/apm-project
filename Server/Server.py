import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import socket
import pickle

from Models.User import User

logging.basicConfig(level=logging.INFO)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serversocket = None

    def start(self):
        # create a socket object
        logging.info("Creating serversocket...")
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind to the port
        self.serversocket.bind((self.host, self.port))

        # queue up to 5 requests
        self.serversocket.listen(5)

        while True:
            logging.info("waiting for a client...")

            # establish a connection
            socket_to_client, addr = self.serversocket.accept()

            logging.info(f"Got a connection from {addr}")

            my_writer_obj = socket_to_client.makefile(mode='rw')

            username = my_writer_obj.readline().rstrip('\n')
            password = my_writer_obj.readline().rstrip('\n')

            is_valid = self.__check_credentials(username, password)
            message = "Login successful\n" if is_valid else "Login failed\n"
            my_writer_obj.write(message)
            my_writer_obj.flush()

            logging.info("Received close message. Closing connection...")
            logging.info("Connection closed with client")
            socket_to_client.close()

    def stop(self):
        if self.serversocket:
            self.serversocket.close()

    def __check_credentials(self, username, password):
        my_reader_obj = open("./Data/users.txt", mode='rb')
        while True:
            try:
                user = pickle.load(my_reader_obj)
                if user.username == username and user.password == password:
                    my_reader_obj.close()
                    return True
            except EOFError:
                break
        my_reader_obj.close()
        return False

if __name__ == "__main__":
    server = Server(socket.gethostname(), 9999)
    server.start()
