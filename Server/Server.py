import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import socket
import pickle
import pandas as pd

from Models.User import User

logging.basicConfig(level=logging.INFO)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serversocket = None
        self.data = pd.read_csv("../Data/Popular_Spotify_Songs.csv")

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

            if is_valid:
                self.handle_client_requests(my_writer_obj)

            logging.info("Received close message. Closing connection...")
            logging.info("Connection closed with client")
            socket_to_client.close()

    def stop(self):
        if self.serversocket:
            self.serversocket.close()

    def __check_credentials(self, username, password):
        my_reader_obj = open("../Data/users.txt", mode='rb')
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

    def handle_client_requests(self, my_writer_obj):
        while True:
            artist = my_writer_obj.readline().rstrip('\n')  # Receive artist's name
            if not artist:
                break
            
            # Process artist's name to get popular songs
            popular_songs = self.__get_popular_songs(artist)

            # Send artist's name and popular songs back to client
            my_writer_obj.write(f"{artist}\n")
            my_writer_obj.write(f"{';'.join(popular_songs)}\n")  # Send popular songs separated by ';'

            # Send message to client indicating success or failure
            if popular_songs:
                my_writer_obj.write("Artist and songs sent successfully\n")
            else:
                my_writer_obj.write("Failed to get popular songs for artist\n")
            my_writer_obj.flush()

    def __get_popular_songs(self, artist):
        artist_data = self.data[self.data['artist(s)_name'].apply(lambda x: artist.lower() in x.lower())]

        if artist_data.empty:
            return []

        # Sort the filtered dataset based on the number of streams in descending order
        sorted_data = artist_data.sort_values(by='streams', ascending=False)

        # Retrieve the top 4 songs from the sorted dataset
        top_songs = sorted_data['track_name'].head(4).tolist()

        print(f"Top songs of {artist}: {top_songs}")

        return top_songs
    
    def __get_popular_year(self, year):
        year_data = self.data[self.data['released_year'] == year]

        if year_data.empty:
            return []

        # Sort the filtered dataset based on the number of streams in descending order
        sorted_data = year_data.sort_values(by='streams', ascending=False)

        # Retrieve the top 4 songs from the sorted dataset
        top_songs = sorted_data[['artist(s)_name', 'track_name']].head(4).values.tolist()

        print(f"Top songs of {year}: {top_songs}")

        return top_songs
    


if __name__ == "__main__":
    server = Server(socket.gethostname(), 9999)
    server.start()
