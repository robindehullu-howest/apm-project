import io
import tkinter as tk
import logging
import socket
import sys
import hashlib
import ast
from PIL import Image, ImageTk

class Application:
    def __init__(self, window):
        self.window = window
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_stream_server = self.socket_to_server.makefile(mode='rw')
        host = socket.gethostname()
        port = 9999

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
        popular_song_str = self.io_stream_server.readline().rstrip('\n')
        
        if popular_song_str:  # Check if the string is not empty
            popular_song_list = ast.literal_eval(popular_song_str)
        
            self.pop_songs_year_listbox.delete(0, tk.END)  # vorige opvraging verwijderen
            for song in popular_song_list:
                artists = ', '.join(ast.literal_eval(song[0]))  # Parse the artist list and join the names together
                song_name = song[1]
                self.pop_songs_year_listbox.insert(tk.END, f"{artists}: {song_name}")
        
            logging.info(f"Year: {year}, Popular Songs: {popular_song_list}")
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

        self.pop_songs_play["text"] = number_of_playlists

        logging.info(f"Song: {song}, Number of Spotify-Playlists: {number_of_playlists}")


#windows for the gui

    def create_login_screen(self):
        # Create the username label and entry
        self.username_label = tk.Label(self.window, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        # Create the password label and entry
        self.password_label = tk.Label(self.window, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        # Create the login button
        self.login_button = tk.Button(self.window, text="Login", command=self.send_login_info)
        self.login_button.pack()

    def create_main_menu(self):
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.login_button.pack_forget()

        self.choice1_button = tk.Button(self.window, text="Get popular songs of artist", command=self.choice1)
        self.choice1_button.pack()

        self.choice2_button = tk.Button(self.window, text="Most popular songs per year", command=self.choice2)
        self.choice2_button.pack()

        self.choice3_button = tk.Button(self.window, text="Number of Spotify-playlists where song is found", command=self.choice3)
        self.choice3_button.pack()

        self.choice4_button = tk.Button(self.window, text="Graph of total streams per year", command=self.choice4)
        self.choice4_button.pack()

    def choice1(self):
        self.artist_window = tk.Toplevel(window)
        self.artist_window.title("Artist")
        self.artist_window.geometry("400x400")

        self.artist_label = tk.Label(self.artist_window, text="Artist:")
        self.artist_label.pack()
        self.artist_entry = tk.Entry(self.artist_window)
        self.artist_entry.pack()

        self.songs_button = tk.Button(self.artist_window, text="Get popular songs for artist", command=self.send_choice1)
        self.songs_button.pack()

        pop_songs_artist_label = tk.Label(self.artist_window, text="Popular Songs:")
        pop_songs_artist_label.pack()

        self.pop_songs_artist_listbox = tk.Listbox(self.artist_window)
        self.pop_songs_artist_listbox.pack()

    def choice2(self):

        self.year_window = tk.Toplevel(window)
        self.year_window.title("popular songs (year)")
        self.year_window.geometry("400x400")

        self.year_label = tk.Label(self.year_window, text="Enter year:")
        self.year_label.pack()
        self.year_entry = tk.Entry(self.year_window)
        self.year_entry.pack()

        self.songs_button = tk.Button(self.year_window, text="Get popular songs", command=self.send_choice2)
        self.songs_button.pack()

        pop_songs_year_label = tk.Label(self.year_window, text="Popular Songs:")
        pop_songs_year_label.pack()

        self.pop_songs_year_listbox = tk.Listbox(self.year_window)
        self.pop_songs_year_listbox.pack()

    def choice3(self):
        self.play_window = tk.Toplevel(window)
        self.play_window.title("Spotify-playlists where song is found")
        self.play_window.geometry("400x400")

        self.play_label = tk.Label(self.play_window, text="Enter song:")
        self.play_label.pack()
        self.play_entry = tk.Entry(self.play_window)
        self.play_entry.pack()

        self.songs_button = tk.Button(self.play_window, text="Get Spotify-playlists", command=self.send_choice3)
        self.songs_button.pack()

        pop_songs_play_label = tk.Label(self.play_window, text="Number of Spotify-Playlists:")
        pop_songs_play_label.pack()

        self.pop_songs_play = tk.Label(self.play_window)
        self.pop_songs_play.pack()

    def choice4(self):
        self.io_stream_server.write("GRAPH\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        graph_image_bytes = self.io_stream_server.read()  # Receive graph image bytes from the server

        # Convert the bytes to an image
        img = Image.open(io.BytesIO(graph_image_bytes))
        img = ImageTk.PhotoImage(img)

        # Display the image in the graph_window
        self.graph_window = tk.Toplevel(window)
        self.graph_window.title("Streams per year")
        self.graph_window.geometry("400x400")

        img_label = tk.Label(self.graph_window, image=img)
        img_label.image = img  # Keep a reference to prevent garbage collection
        img_label.pack()

    def close_connection(self):
        logging.info("Close connection with server...")
        self.io_stream_server.write("CLOSE\n")
        self.io_stream_server.flush()
        self.io_stream_server.close()
        self.socket_to_server.close()


# Set up logging
logging.basicConfig(level=logging.INFO)

# Create the main window
window = tk.Tk()
window.title("GUI Client")

# Create the application
app = Application(window)

# Start the main loop
window.mainloop()

# Close the connection
app.close_connection()