import io
import json
import logging
import os
import sys
import threading
import base64
import ast
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Models.User import User

SPOTIFY_DATA_PATH = "./Data/spotify_data.csv"
USERS_PATH = "./Data/users.txt"
LOGGED_USERS_PATH = "./Data/logged_users.txt"

SEARCH_COUNTS = {
    "ARTIST": 0,
    "YEAR": 0,
    "PLAYLIST": 0,
    "GRAPH": 0
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
        topic = self.read_line_from_client()

        command_handlers = {
            "LOGIN": self.__handle_login,
            "REGISTRATION": self.__handle_register,
            "ARTIST": self.__handle_artist,
            "YEAR": self.__handle_year,
            "PLAYLIST": self.__handle_playlist,
            "GRAPH": self.__handle_graph
        }

        while not (topic == "CLOSE" or self.server_closing):
            global SEARCH_COUNTS

            self.__print_message_gui_server(f"Command received: {topic}")

            if topic in command_handlers:
                command_handlers[topic]()
            if topic in SEARCH_COUNTS:
                SEARCH_COUNTS[topic] += 1
                self.__print_message_gui_server(f"Times requested: Artist: {SEARCH_COUNTS['ARTIST']}, Year: {SEARCH_COUNTS['YEAR']}, Playlist: {SEARCH_COUNTS['PLAYLIST']}, Graph: {SEARCH_COUNTS['GRAPH']}")


            topic = self.read_line_from_client()

        self.__print_message_gui_server("Connection with client closed...")
        self.io_stream_client.close()
        self.socket_to_client.close()

    def close_socket(self):
        self.server_closing = True

    def send_messages(self, topic: str, messages: List):
        self.io_stream_client.write(f"{topic}\n")
        for message in messages:
            self.io_stream_client.write(f"{message}\n")
        self.io_stream_client.flush()

    def __handle_login(self):
        identifier = self.read_line_from_client()
        password = self.read_line_from_client()
        user = User(identifier, identifier, password)
        is_valid = self.__check_credentials(user)
        message = "Login successful" if is_valid else "Login failed"
        self.send_messages("LOGIN", [message])
        self.__print_message_gui_server(message)

        if is_valid:
            self.__store_logged_user(identifier)

    def __store_logged_user(self, identifier: str):
        with open(LOGGED_USERS_PATH, "a") as file:
            file.write(f"Identifier: {identifier}\n")
    
    def __check_credentials(self, input_user: User):
        with open(USERS_PATH, mode='rb') as my_reader_obj:
            while True:
                try:
                    stored_user = pickle.load(my_reader_obj)
                    if stored_user == input_user:
                        return True
                except EOFError:
                    break
        return False

    def __handle_register(self):
        user_details = ['username', 'nickname', 'email', 'password']
        user_info = {detail: self.read_line_from_client() for detail in user_details}

        self.__register_user(user_info['username'], user_info['email'], user_info['password'], user_info['nickname'])
        message = "Registration successful"
        self.send_messages("REGISTRATION", [message])
        self.__print_message_gui_server(message)

    @staticmethod
    def __register_user(username: str, email: str, password: str, nickname: str):
        user = User(username, email, password, nickname)
        with open(USERS_PATH, mode='ab') as my_writer_obj:
            pickle.dump(user, my_writer_obj)

    def __handle_artist(self):
        artist = self.read_line_from_client()
        popular_songs = self.__get_popular_songs_of_artist(artist)
        self.send_messages("ARTIST", [popular_songs])

    def __get_popular_songs_of_artist(self, artist):
        artist_data = self.data[self.data['artist(s)_name'].apply(lambda x: artist.lower() in x.lower())]

        if artist_data.empty:
            return "No songs found."

        sorted_data = artist_data.sort_values(by='streams', ascending=False)

        top_songs = sorted_data['track_name'].head(5).tolist()
        top_songs = ';'.join(top_songs)

        return top_songs
    
    def __handle_year(self):
        year = int(self.read_line_from_client())
        popular_songs = json.dumps(self.__get_popular_songs_of_year(year))
        self.send_messages("YEAR", [popular_songs])

    def __get_popular_songs_of_year(self, year) -> dict:
        year_data = self.data[self.data['released_year'] == year]

        if year_data.empty:
            return "No songs found."

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
        song = self.read_line_from_client()
        number_playlists = self.__get_playlists_of_song(song)

        self.send_messages("PLAYLIST", [number_playlists])


    def __get_playlists_of_song(self, song):
        playlist_data = self.data[self.data['track_name'].str.lower() == song.lower()]

        if playlist_data.empty:
            return "No playlists found."
        
        number_playlists = playlist_data.iloc[0]['in_spotify_playlists']
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

        self.send_messages("GRAPH", [img_string])

    def read_line_from_client(self):
        return self.io_stream_client.readline().rstrip('\n')

    def __print_message_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")