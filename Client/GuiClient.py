import tkinter as tk
import logging
import socket
import sys
import hashlib

class Application:
    def __init__(self, window):
        self.window = window
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 9999

        logging.info("Making connection with server...")
        self.socket_to_server.connect((host, port))

        self.create_login_screen()

    def send_login_info(self):
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()
        io_stream_server = self.socket_to_server.makefile(mode='rw')
        io_stream_server.write(f"{username}\n")
        io_stream_server.write(f"{password}\n")
        io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        message = io_stream_server.readline().rstrip('\n')
        logging.info(f"Message from server: {message}")

        if message == "Login successful":
            self.create_main_menu()


    def send_choice1(self):
        artist = self.artist_entry.get()
        io_stream_server = self.socket_to_server.makefile(mode='rw')
        io_stream_server.write(f"{artist}\n")
        io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        artist_name = io_stream_server.readline().rstrip('\n') 
        popular_songs_str = io_stream_server.readline().rstrip('\n')
        popular_songs = popular_songs_str.split(';') 

        logging.info(f"Artist: {artist_name}, Popular Songs: {popular_songs}")

        self.popular_songs_listbox.delete(0, tk.END) #vorige opvraging verwijderen
        for song in popular_songs:
            self.popular_songs_listbox.insert(tk.END, song)

    def send_choice2(self):
        year = self.artist_entry.get()
        io_stream_server = self.socket_to_server.makefile(mode='rw')
        io_stream_server.write(f"{year}\n")
        io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        year = io_stream_server.readline().rstrip('\n') 
        popular_song_str = io_stream_server.readline().rstrip('\n')
        popular_song = popular_song_str.split(';') 

        logging.info(f"Year: {year}, Popular Song: {popular_song}")



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


        self.artist_label = tk.Label(self.artist_window, text="Artist:")
        self.artist_label.pack()
        self.artist_entry = tk.Entry(self.artist_window)
        self.artist_entry.pack()


        self.songs_button = tk.Button(self.artist_window, text="Get popular songs for artist", command=self.send_choice1)
        self.songs_button.pack()

        self.popular_songs_label = tk.Label(self.artist_window, text="Popular Songs:")
        self.popular_songs_label.pack()

        self.popular_songs_listbox = tk.Listbox(self.artist_window)
        self.popular_songs_listbox.pack()


    def choice2(self):
        self.year_window = tk.Toplevel(window)
        self.year_window.title("popular songs (year)")

        self.year_label = tk.Label(self.year_window, text="Enter year:")
        self.year_label.pack()
        self.year_entry = tk.Entry(self.year_window)
        self.year_entry.pack()

        self.songs_button = tk.Button(self.year_window, text="Get popular songs", command=self.send_choice2)
        self.songs_button.pack()


    def choice3(self):
        pass


    def close_connection(self):
        logging.info("Close connection with server...")
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