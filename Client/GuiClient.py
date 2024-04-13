import io
import tkinter as tk
from tkinter import ttk
import logging
import socket
import sys
import hashlib
import ast
from PIL import Image, ImageTk
import base64
import json

class Application:
    def __init__(self, window):
        self.window = window
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_stream_server = self.socket_to_server.makefile(mode='rw')
        host = socket.gethostname()
        port = 9999

        self.messages = {}
        self.answers = {}
        

        logging.info("Making connection with server...")
        self.socket_to_server.connect((host, port))

        self.window.geometry("600x400")

        self.create_login_screen()

#functions for the gui

    def send_login_info(self):
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()
        self.io_stream_server.write("LOGIN\n")
        self.io_stream_server.write(f"{username}\n")
        self.io_stream_server.write(f"{password}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        message = self.io_stream_server.readline().rstrip('\n')
        logging.info(f"Message from server: {message}")

        if message == "Login successful":
            self.create_main_menu()

    def send_choice1(self):
        artist = self.artist_entry.get()
        self.io_stream_server.write("ARTIST\n")
        self.io_stream_server.write(f"{artist}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        artist_name = self.io_stream_server.readline().rstrip('\n') 
        popular_songs_str = self.io_stream_server.readline().rstrip('\n')
        popular_songs = popular_songs_str.split(';') 

        logging.info(f"Artist: {artist_name}, Popular Songs: {popular_songs}")

        self.messages["choice1"] = "ARTIST"
        self.answers["choice1"] = {"artist_name": artist_name, "popular_songs": popular_songs}

        self.pop_songs_artist_listbox.delete(0, tk.END) #vorige opvraging verwijderen
        for song in popular_songs:
            self.pop_songs_artist_listbox.insert(tk.END, song)

    def send_choice2(self):
        year = self.year_entry.get()
        self.io_stream_server.write("YEAR\n")
        self.io_stream_server.write(f"{year}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        year = self.io_stream_server.readline().rstrip('\n') 
        pop_songs_str = self.io_stream_server.readline().rstrip('\n')
        
        if pop_songs_str:
            self.pop_songs_year_listbox.delete(0, tk.END)  # vorige opvraging verwijderen
            try:
                pop_songs_json = json.loads(pop_songs_str)
                for song, artists in pop_songs_json.items():
                    self.pop_songs_year_listbox.insert(tk.END, f"{', '.join(artists)}: {song}")

            except Exception as e:
                self.pop_songs_year_listbox.insert(tk.END, pop_songs_str)
                logging.error(f"Error: {e}")

        else:
            logging.info(f"No popular songs received for the year: {year}")

    def send_choice3(self):
        song = self.play_entry.get()
        self.io_stream_server.write("PLAYLIST\n")
        self.io_stream_server.write(f"{song}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        song = self.io_stream_server.readline().rstrip('\n') 
        number_of_playlists = self.io_stream_server.readline().rstrip('\n')

        self.messages["choice3"] = "PLAYLIST"
        self.answers["choice3"] = {"song": song, "number_of_playlists": number_of_playlists}

        self.pop_songs_play["text"] = number_of_playlists

        logging.info(f"Song: {song}, Number of Spotify-Playlists: {number_of_playlists}")


#windows for the gui

    def create_login_screen(self):
        self.username_label = tk.Label(self.window, text="Username:", bg="#2d2d3d", fg="white")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        self.password_label = tk.Label(self.window, text="Password:", bg="#2d2d3d", fg="white")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.window, text="Login", command=self.send_login_info, bg="#7474ab", fg="white")
        self.login_button.pack()

    def create_main_menu(self):
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.login_button.pack_forget()

        self.choice1_button = tk.Button(self.window, text="Get popular songs of artist", command=self.choice1, bg="#7474ab", fg="white")
        self.choice1_button.pack()

        self.choice2_button = tk.Button(self.window, text="Most popular songs per year", command=self.choice2, bg="#7474ab", fg="white")
        self.choice2_button.pack()

        self.choice3_button = tk.Button(self.window, text="Number of Spotify-playlists where song is found", command=self.choice3, bg="#7474ab", fg="white")
        self.choice3_button.pack()

        self.choice4_button = tk.Button(self.window, text="Graph of total streams per year", command=self.choice4, bg="#7474ab", fg="white")
        self.choice4_button.pack()

    def choice1(self):
        self.artist_window = tk.Toplevel(window)
        self.artist_window.title("Artist")
        self.artist_window.geometry("400x400")
        self.artist_window.configure(bg="#2d2d3d")

        self.artist_label = tk.Label(self.artist_window, text="Artist:", bg="#2d2d3d", fg="white")
        self.artist_label.pack()
        self.artist_entry = tk.Entry(self.artist_window)
        self.artist_entry.pack()

        self.songs_button = tk.Button(self.artist_window, text="Get popular songs for artist", command=self.send_choice1, bg="#7474ab", fg="white")
        self.songs_button.pack()

        pop_songs_artist_label = tk.Label(self.artist_window, text="Popular Songs:", bg="#2d2d3d", fg="white")
        pop_songs_artist_label.pack()

        self.pop_songs_artist_listbox = tk.Listbox(self.artist_window)
        self.pop_songs_artist_listbox.pack()

    def choice2(self):
        self.year_window = tk.Toplevel(window)
        self.year_window.title("popular songs (year)")
        self.year_window.geometry("400x400")
        self.year_window.configure(bg="#2d2d3d")

        self.year_label = tk.Label(self.year_window, text="Enter year:", bg="#2d2d3d", fg="white")
        self.year_label.pack()
        self.year_entry = tk.Entry(self.year_window)
        self.year_entry.pack()

        self.songs_button = tk.Button(self.year_window, text="Get popular songs", command=self.send_choice2, bg="#7474ab", fg="white")
        self.songs_button.pack()

        pop_songs_year_label = tk.Label(self.year_window, text="Popular Songs:", bg="#2d2d3d", fg="white")
        pop_songs_year_label.pack()

        self.pop_songs_year_listbox = tk.Listbox(self.year_window)
        self.pop_songs_year_listbox.pack()

    def choice3(self):
        self.play_window = tk.Toplevel(window)
        self.play_window.title("Spotify-playlists where song is found")
        self.play_window.geometry("400x400")
        self.play_window.configure(bg="#2d2d3d")


        self.play_label = tk.Label(self.play_window, text="Enter song:", bg="#2d2d3d", fg="white")
        self.play_label.pack()
        self.play_entry = tk.Entry(self.play_window)
        self.play_entry.pack()

        self.songs_button = tk.Button(self.play_window, text="Get Spotify-playlists", command=self.send_choice3, bg="#7474ab", fg="white")
        self.songs_button.pack()

        pop_songs_play_label = tk.Label(self.play_window, text="Number of Spotify-Playlists:", bg="#2d2d3d", fg="white")
        pop_songs_play_label.pack()

        self.pop_songs_play = tk.Label(self.play_window)
        self.pop_songs_play.pack()

    def choice4(self):
        self.io_stream_server.write("GRAPH\n")
        self.io_stream_server.flush()

        logging.info("Waiting for graph from server...")
        img_string = self.io_stream_server.readline().rstrip('\n')

        img_bytes = base64.b64decode(img_string)

        img = Image.open(io.BytesIO(img_bytes))

        window_width = 800
        window_height = 600
        img = img.resize((window_width, window_height))
        img = ImageTk.PhotoImage(img)

        self.graph_window = tk.Toplevel(window)
        self.graph_window.title("Streams per year")
        self.graph_window.geometry("900x700")
        self.graph_window.configure(bg="#2d2d3d")


        img_label = tk.Label(self.graph_window, image=img)
        img_label.image = img
        img_label.pack()


    def close_connection(self):
        logging.info("Close connection with server...")
        self.io_stream_server.write("CLOSE\n")
        self.io_stream_server.flush()
        self.io_stream_server.close()
        self.socket_to_server.close()


logging.basicConfig(level=logging.INFO)

window = tk.Tk()
window.title("GUI Client")

window.configure(bg="#2d2d3d") 

app = Application(window)

window.mainloop()

app.close_connection()