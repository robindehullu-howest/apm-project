import logging
import socket

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

            my_writer_obj.write(f"{username}\n")
            my_writer_obj.write(f"{password}\n")
            my_writer_obj.flush()

            logging.info("Received close message. Closing connection...")
            logging.info("Connection closed with client")
            socket_to_client.close()

    def stop(self):
        if self.serversocket:
            self.serversocket.close()

# Usage example:
if __name__ == "__main__":
    server = Server(socket.gethostname(), 9999)
    server.start()