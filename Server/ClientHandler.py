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
    
    # def handle_client_requests(self, my_writer_obj):
    # while True:
    #     artist = my_writer_obj.readline().rstrip('\n')  # Receive artist's name
    #     if not artist:
    #         break
        
    #     # Process artist's name to get popular songs
    #     popular_songs = self.__get_popular_songs(artist)

    #     # Send artist's name and popular songs back to client
    #     my_writer_obj.write(f"{artist}\n")
    #     my_writer_obj.write(f"{';'.join(popular_songs)}\n")  # Send popular songs separated by ';'

    #     # Send message to client indicating success or failure
    #     if popular_songs:
    #         my_writer_obj.write("Artist and songs sent successfully\n")
    #     else:
    #         my_writer_obj.write("Failed to get popular songs for artist\n")
    #     my_writer_obj.flush()

    # def __get_popular_songs(self, artist):
    #     artist_data = self.data[self.data['artist(s)_name'].apply(lambda x: artist.lower() in x.lower())]

    #     if artist_data.empty:
    #         return []

    #     # Sort the filtered dataset based on the number of streams in descending order
    #     sorted_data = artist_data.sort_values(by='streams', ascending=False)

    #     # Retrieve the top 4 songs from the sorted dataset
    #     top_songs = sorted_data['track_name'].head(4).tolist()

    #     print(f"Top songs of {artist}: {top_songs}")

    #     return top_songs
    
    # def __get_popular_year(self, year):
    #     year_data = self.data[self.data['released_year'] == year]

    #     if year_data.empty:
    #         return []

    #     # Sort the filtered dataset based on the number of streams in descending order
    #     sorted_data = year_data.sort_values(by='streams', ascending=False)

    #     # Retrieve the top 4 songs from the sorted dataset
    #     top_songs = sorted_data[['artist(s)_name', 'track_name']].head(4).values.tolist()

    #     print(f"Top songs of {year}: {top_songs}")

    #     return top_songs

    def __print_message_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")