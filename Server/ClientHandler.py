import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import json
import logging
import ast
import hashlib

from Models.User import User

SPOTIFY_DATA_PATH = "./Data/spotify_data.csv"
USERS_PATH = "./Data/users.txt"
LOGGED_USERS_PATH = "./Data/logged_users.txt"

search_counts = {
    "Artiest": 0,
    "Jaar": 0,
    "Playlist": 0,
    "Graph": 0
}

class ClientHandler(threading.Thread):
    clienthandler_count = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        self.socket_to_client = socketclient
        self.io_stream_client = self.socket_to_client.makefile(mode='rw')
        self.messages_queue = messages_queue
        self.data = pd.read_csv(SPOTIFY_DATA_PATH)
        self.id = ClientHandler.clienthandler_count
        ClientHandler.clienthandler_count += 1
        self.server_closing = False

    def run(self):
        self.__print_message_gui_server("Started & waiting...")
        command = self.io_stream_client.readline().rstrip('\n')
        while not (command == "CLOSE" or self.server_closing):
            self.__print_message_gui_server(f"Command received: {command}")
            global search_counts
            if command == "LOGIN":
                self.__handle_login()
            elif command == "REGISTER":
                self.__handle_register()
            elif command == "ARTIST":
                self.__handle_artist()
                search_counts["Artiest"] += 1
            elif command == "YEAR":
                self.__handle_year()
                search_counts["Jaar"] += 1
            elif command == "PLAYLIST":
                self.__handle_playlist()
                search_counts["Playlist"] += 1
            elif command == "GRAPH":
                self.__handle_graph()
                search_counts["Graph"] += 1

            self.__print_message_gui_server(f"Times requested: Artist: {search_counts['Artiest']}, Year: {search_counts['Jaar']}, Playlist: {search_counts['Playlist']}, Graph: {search_counts['Graph']}")

            command = self.io_stream_client.readline().rstrip('\n')

        self.__print_message_gui_server("Connection with client closed...")
        self.io_stream_client.close()
        self.socket_to_client.close()

    def close_socket(self):
        self.server_closing = True

    @staticmethod
    def __register_user(username: str, email: str, password: str, nickname: str):
        user = User(username, email, password, nickname)
        with open(USERS_PATH, mode='ab') as my_writer_obj:
            pickle.dump(user, my_writer_obj)

    def __handle_login(self):
        identifier = self.io_stream_client.readline().rstrip('\n')
        password = self.io_stream_client.readline().rstrip('\n')
        is_valid = self.__check_credentials(User(identifier, identifier, password))
        message = "Login successful\n" if is_valid else "Login failed\n"
        self.io_stream_client.write(message)
        self.io_stream_client.flush()
        self.__print_message_gui_server(message)

        if is_valid:
            self.__store_logged_user(identifier)

    def __handle_register(self):
        username = self.io_stream_client.readline().rstrip('\n')
        nickname = self.io_stream_client.readline().rstrip('\n')
        email = self.io_stream_client.readline().rstrip('\n')
        password = self.io_stream_client.readline().rstrip('\n')

        self.__register_user(username, email, password, nickname)
        message = "Registration successful\n"
        self.io_stream_client.write(message)
        self.io_stream_client.flush()
        self.__print_message_gui_server(message)

    def __store_logged_user(self, identifier: str):
        with open(LOGGED_USERS_PATH, "a") as file:
            file.write(f"Username: {identifier}\n")
    
    def __check_credentials(self, input_user: User):
        with open(USERS_PATH, mode='rb') as my_reader_obj:
            while True:
                try:
                    stored_user = pickle.load(my_reader_obj)
                    print(f"Stored user: {stored_user}")
                    print(f"Input user: {input_user}")
                    if stored_user == input_user:
                        return True
                except EOFError:
                    break
        return False

    def __handle_artist(self):
        artist = self.io_stream_client.readline().rstrip('\n')
        popular_songs = self.__get_popular_songs_of_artist(artist)

        self.io_stream_client.write(f"{artist}\n")
        if popular_songs is not None:
            self.io_stream_client.write(f"{';'.join(popular_songs)}\n")
            # self.io_stream_client.write("Artist and songs sent successfully\n")
        else:
            self.io_stream_client.write("No songs found.\n")
        self.io_stream_client.flush()

    def __get_popular_songs_of_artist(self, artist):
        artist_data = self.data[self.data['artist(s)_name'].apply(lambda x: artist.lower() in x.lower())]

        if artist_data.empty:
            return None

        sorted_data = artist_data.sort_values(by='streams', ascending=False)

        top_songs = sorted_data['track_name'].head(5).tolist()

        print(f"Top songs of {artist}: {top_songs}")

        return top_songs
    
    def __handle_year(self):
        year = int(self.io_stream_client.readline().rstrip('\n'))
        popular_songs = self.__get_popular_songs_of_year(year)

        self.io_stream_client.write(f"{year}\n")
        if popular_songs is not None:
            popular_songs_json = json.dumps(popular_songs)
            self.io_stream_client.write(popular_songs_json + "\n")
        else:
            self.io_stream_client.write("No songs found.\n")
        self.io_stream_client.flush()

    def __get_popular_songs_of_year(self, year) -> dict:
        year_data = self.data[self.data['released_year'] == year]

        if year_data.empty:
            return None

        sorted_data = year_data.sort_values(by='streams', ascending=False)

        top_songs_data = sorted_data[['artist(s)_name', 'track_name']].head(4)
        top_songs = top_songs_data.values.tolist()

        top_songs_dict = {}
        for song_detail in top_songs:
            artists_str, song_name = song_detail
            top_songs_dict[song_name] = []
            artists = ast.literal_eval(artists_str)
            for artist in artists:
                artist = artist.strip("[]'")
                top_songs_dict[song_name].append(artist)

        logging.info(top_songs_dict)
        return top_songs_dict

    def __handle_playlist(self):
        song = self.io_stream_client.readline().rstrip('\n')
        number_playlists = self.__get_playlists_of_song(song)

        if number_playlists is not None:
            self.io_stream_client.write(f"{number_playlists}\n")
        else:
            self.io_stream_client.write("No playlists found.\n")
        
        self.io_stream_client.flush()


    def __get_playlists_of_song(self, song):
        playlist_data = self.data[self.data['track_name'].str.lower() == song.lower()]

        if playlist_data.empty:
            return None
        
        number_playlists = playlist_data.iloc[0]['in_spotify_playlists']
        logging.info(f"Number of Spotify playlists for '{song}': {number_playlists}")
        return number_playlists


    def __handle_graph(self):
        year_streams = self.data.groupby('released_year')['streams'].sum()
        plt.style.use('dark_background')

        plt.figure(figsize=(8, 6), facecolor='#191414')
        year_streams.plot(kind='bar',color='#1DB954')

        plt.xlabel('Year',color='#1DB954')
        plt.ylabel('Total Streams',color='#1DB954')
        plt.title('Total Streams per Year',color='#1DB954')

        plt.xticks(color='white')
        plt.yticks(color='white')

        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)

        img_string = base64.b64encode(img_bytes.read()).decode()

        self.io_stream_client.write(f"{img_string}\n")
        self.io_stream_client.flush()


    def __print_message_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")