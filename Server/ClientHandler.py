import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import pickle
import pandas as pd

from Models.User import User

class ClientHandler(threading.Thread):
    clienthandler_count = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        self.socket_to_client = socketclient
        self.io_stream_client = self.socket_to_client.makefile(mode='rw')
        self.messages_queue = messages_queue
        self.data = pd.read_csv("../Data/spotify_data.csv")
        self.id = ClientHandler.clienthandler_count
        ClientHandler.clienthandler_count += 1

    def run(self):
        self.__print_message_gui_server("Started & waiting...")
        command = self.io_stream_client.readline().rstrip('\n')
        while command != "CLOSE":
            self.__print_message_gui_server(f"Command received: {command}")

            if command == "LOGIN":
                self.__handle_login()
            elif command == "ARTIST":
                self.__handle_artist()
            elif command == "YEAR":
                self.__handle_year()
            elif command == "PLAYLIST":
                self.__handle_playlist()

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
        my_reader_obj = open("../Data/users.txt", mode='rb')
        while True:
            try:
                stored_user = pickle.load(my_reader_obj)
                if stored_user == input_user:
                    my_reader_obj.close()
                    return True
            except EOFError:
                break
    
    def __handle_artist(self):
        artist = self.io_stream_client.readline().rstrip('\n')
        popular_songs = self.__get_popular_songs_of_artist(artist)

        self.io_stream_client.write(f"{artist}\n")
        self.io_stream_client.write(f"{';'.join(popular_songs)}\n")
        self.io_stream_client.write("Artist and songs sent successfully\n" if popular_songs else f"Failed to get popular songs for artist {artist}\n")
        self.io_stream_client.flush()

    def __get_popular_songs_of_artist(self, artist):
        artist_data = self.data[self.data['artist(s)_name'].apply(lambda x: artist.lower() in x.lower())]

        if artist_data.empty:
            return None

        # Sort the filtered dataset based on the number of streams in descending order
        sorted_data = artist_data.sort_values(by='streams', ascending=False)

        # Retrieve the top 4 songs from the sorted dataset
        top_songs = sorted_data['track_name'].head(4).tolist()

        print(f"Top songs of {artist}: {top_songs}")

        return top_songs
    
    def __handle_year(self):
        year = int(self.io_stream_client.readline().rstrip('\n'))
        popular_songs = self.__get_popular_songs_of_year(year)

        self.io_stream_client.write(f"{year}\n")
        self.io_stream_client.write(f"{popular_songs}\n")
        self.io_stream_client.flush()
    
    def __get_popular_songs_of_year(self, year):
        year_data = self.data[self.data['released_year'] == year]

        if year_data.empty:
            return None

        # Sort the filtered dataset based on the number of streams in descending order
        sorted_data = year_data.sort_values(by='streams', ascending=False)

        # Retrieve the top 4 songs from the sorted dataset
        top_songs = sorted_data[['artist(s)_name', 'track_name']].head(4).values.tolist()

        print(f"Top songs of {year}: {top_songs}")

        return top_songs

    def __handle_playlist(self):
        song = self.io_stream_client.readline().rstrip('\n')
        playlists = self.__get_playlists_of_song(song)

        self.io_stream_client.write(f"{song}\n")
        self.io_stream_client.write(f"{playlists}\n")
        self.io_stream_client.flush()


    def __get_playlists_of_song(self, song):
        # Filter the dataset to include only rows where the track name matches the input song
        playlist_data = self.data[self.data['track_name'] == song]

        if playlist_data.empty:
            return None
        
        # Count the number of playlists the song appears in
        number_playlists = playlist_data['in_spotify_playlists']

        print(f"Number of Spotify playlists {song} is in: {number_playlists}")

        return number_playlists


    def __print_message_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")