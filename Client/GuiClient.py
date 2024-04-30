import io
import os
import tkinter as tk
from tkinter import ttk
import logging
import socket
import hashlib
from PIL import Image, ImageTk
import base64
import json

BUTTON_COLOR = "#1DB954"
BUTTON_COLOR_ENTER = "#1ED760"
BACKGROUND_COLOR = "#191414"

class RoundedButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(relief=tk.FLAT, bg=BUTTON_COLOR, fg="white", bd=0)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        self.config(bg=BUTTON_COLOR_ENTER)

    def on_leave(self, event):
        self.config(bg=BUTTON_COLOR)

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

    def clear_table(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)


    # Sending data to server

    def send_login_info(self):
        identifier = self.identifier_entry.get()
        password = hashlib.sha256(self.login_password_entry.get().encode()).hexdigest()

        self.io_stream_server.write("LOGIN\n")
        self.io_stream_server.write(f"{identifier}\n")
        self.io_stream_server.write(f"{password}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        message = self.io_stream_server.readline().rstrip('\n')
        logging.info(f"Message from server: {message}")

        if message == "Login successful":
            self.create_main_menu()

    def send_register_info(self):
        username = self.register_username_entry.get()
        nickname = self.register_nickname_entry.get()
        email = self.register_email_entry.get()
        password = hashlib.sha256(self.register_password_entry.get().encode()).hexdigest()

        self.io_stream_server.write("REGISTER\n")
        self.io_stream_server.write(f"{username}\n")
        self.io_stream_server.write(f"{nickname}\n")
        self.io_stream_server.write(f"{email}\n")
        self.io_stream_server.write(f"{password}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        message = self.io_stream_server.readline().rstrip('\n')
        logging.info(f"Message from server: {message}")

        self.register_window.destroy()

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

        self.clear_table(self.pop_songs_artist_tree)

        for index, song in enumerate(popular_songs, start=1):
            self.pop_songs_artist_tree.insert('', 'end',text=index, values=[song])

    def send_choice2(self):
        year = self.year_entry.get()
        self.io_stream_server.write("YEAR\n")
        self.io_stream_server.write(f"{year}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        year = self.io_stream_server.readline().rstrip('\n') 
        pop_songs_str = self.io_stream_server.readline().rstrip('\n')
        
        if pop_songs_str:
            self.clear_table(self.pop_songs_year_tree)  # vorige opvraging verwijderen
            try:
                pop_songs_json = json.loads(pop_songs_str)
                for index, (song, artists) in enumerate(pop_songs_json.items(), start=1):
                    self.pop_songs_year_tree.insert('', 'end', text=index, values=[song, artists])

            except Exception as e:
                self.pop_songs_year_tree.insert('', 'end', values=[pop_songs_str])  # Insert error message directly into treeview
                logging.error(f"Error: {e}")

        else:
            logging.info(f"No popular songs received for the year: {year}")

    def send_choice3(self):
        song = self.play_entry.get()
        self.io_stream_server.write("PLAYLIST\n")
        self.io_stream_server.write(f"{song}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")
        number_of_playlists = self.io_stream_server.readline().rstrip('\n')
        if number_of_playlists == "No playlists found.":
            self.pop_songs_play["text"] = number_of_playlists
            logging.info("No playlists found.")
        else:
            self.pop_songs_play["text"] = number_of_playlists
            logging.info(f"Number of Spotify-Playlists: {number_of_playlists}")




    # Window creation functions

    def create_login_screen(self):
        frame = tk.Frame(self.window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.identifier_label = tk.Label(frame, text="Username or email:", bg=BACKGROUND_COLOR, fg="white")
        self.identifier_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.identifier_entry = tk.Entry(frame)
        self.identifier_entry.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.password_label = tk.Label(frame, text="Password:", bg=BACKGROUND_COLOR, fg="white")
        self.password_label.grid(row=2, column=0, pady=(5, 2), sticky="w")

        self.login_password_entry = tk.Entry(frame, show="*")
        self.login_password_entry.grid(row=3, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.login_button = RoundedButton(frame, text="Login", command=self.send_login_info, bg=BUTTON_COLOR, fg="white")
        self.login_button.grid(row=4, column=0, pady=5)

        self.register_window_button = RoundedButton(frame, text="Register", command=self.create_register_screen, bg=BUTTON_COLOR, fg="white")
        self.register_window_button.grid(row=5, column=0, pady=5)

    def create_register_screen(self):
        self.register_window = tk.Toplevel(window)
        self.register_window.title("Register user")
        self.register_window.geometry("400x400")
        self.register_window.configure(bg=BACKGROUND_COLOR)

        self.register_username_label = tk.Label(self.register_window, text="Username:", bg=BACKGROUND_COLOR, fg="white")
        self.register_username_label.pack()

        self.register_username_entry = tk.Entry(self.register_window)
        self.register_username_entry.pack()

        self.register_nickname_label = tk.Label(self.register_window, text="Nickname:", bg=BACKGROUND_COLOR, fg="white")
        self.register_nickname_label.pack()

        self.register_nickname_entry = tk.Entry(self.register_window)
        self.register_nickname_entry.pack()

        self.register_email_label = tk.Label(self.register_window, text="Email:", bg=BACKGROUND_COLOR, fg="white")
        self.register_email_label.pack()

        self.register_email_entry = tk.Entry(self.register_window)
        self.register_email_entry.pack()

        self.register_password_label = tk.Label(self.register_window, text="Password:", bg=BACKGROUND_COLOR, fg="white")
        self.register_password_label.pack()

        self.register_password_entry = tk.Entry(self.register_window, show="*")
        self.register_password_entry.pack()

        self.register_button = RoundedButton(self.register_window, text="Register", command=self.send_register_info, bg=BUTTON_COLOR, fg="white")
        self.register_button.pack()

    def create_main_menu(self):
        # Hide previous widgets
        self.identifier_label.pack_forget()
        self.identifier_entry.pack_forget()
        self.password_label.pack_forget()
        self.login_password_entry.pack_forget()
        self.login_button.pack_forget()
        self.register_window_button.pack_forget()
    
        # Set window geometry
        self.window.geometry("1000x600")
    
        # Load and display image
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "Images", "spotify-logo.png")
        self.img = ImageTk.PhotoImage(Image.open(image_path))
        self.img_label = tk.Label(self.window, image=self.img, bg=BACKGROUND_COLOR)
        self.img_label.grid(row=0, column=0, columnspan=2, pady=5)  # over 2 kolommen
    
        # Define button font
        button_font = ("Arial", 12, "bold")
    
        # Create and place buttons
        self.choice1_button = RoundedButton(self.window, text="Get popular songs of artist", command=self.choice1, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=button_font)
        self.choice1_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
        self.choice2_button = RoundedButton(self.window, text="Most popular songs per year", command=self.choice2, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=button_font)
        self.choice2_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
        self.choice3_button = RoundedButton(self.window, text="Number of Spotify-playlists where song is found", command=self.choice3, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=button_font)
        self.choice3_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    
        self.choice4_button = RoundedButton(self.window, text="Graph of total streams per year", command=self.choice4, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=button_font)
        self.choice4_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        # Configure column weights to center the widgets
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)


    # Button callback functions

    def choice1(self):
        self.artist_window = tk.Toplevel(window)
        self.artist_window.title("Artist")
        self.artist_window.geometry("400x400")
        self.artist_window.configure(bg=BACKGROUND_COLOR)

        self.artist_label = tk.Label(self.artist_window, text="Artist:", bg=BACKGROUND_COLOR, fg="white")
        self.artist_label.pack()
        self.artist_entry = tk.Entry(self.artist_window)
        self.artist_entry.pack()
        # w = Spinbox(self.artist_window, from_=0, to=50)
        # w.pack()

        self.songs_button = RoundedButton(self.artist_window, text="Get popular songs for artist", command=self.send_choice1, bg=BUTTON_COLOR, fg="white")
        self.songs_button.pack()

        pop_songs_artist_label = tk.Label(self.artist_window, text="Popular Songs:", bg=BACKGROUND_COLOR, fg="white")
        pop_songs_artist_label.pack()

        self.pop_songs_artist_tree = ttk.Treeview(self.artist_window, columns=('Number','Popular Songs'))
        self.pop_songs_artist_tree.heading('#0', text='Number')
        self.pop_songs_artist_tree.heading('#1', text='Popular Songs')
        self.pop_songs_artist_tree.pack()

    def choice2(self):
        self.year_window = tk.Toplevel(window)
        self.year_window.title("popular songs (year)")
        self.year_window.geometry("400x400")
        self.year_window.configure(bg=BACKGROUND_COLOR)

        self.year_label = tk.Label(self.year_window, text="Enter year:", bg=BACKGROUND_COLOR, fg="white")
        self.year_label.pack()
        self.year_entry = tk.Entry(self.year_window)
        self.year_entry.pack()
        # w = Spinbox(self.year_window, from_=0, to=50)
        # w.pack()

        self.songs_button = RoundedButton(self.year_window, text="Get popular songs", command=self.send_choice2, bg=BUTTON_COLOR, fg="white")
        self.songs_button.pack()

        pop_songs_year_label = tk.Label(self.year_window, text="Popular Songs:", bg=BACKGROUND_COLOR, fg="white")
        pop_songs_year_label.pack()

        self.pop_songs_year_tree = ttk.Treeview(self.year_window, columns=('Number','Popular Songs','Artist(s)'))
        self.pop_songs_year_tree.heading('#0', text='Number')
        self.pop_songs_year_tree.heading('#1', text='Popular Songs')
        self.pop_songs_year_tree.heading('#2', text='Artist(s)')
        self.pop_songs_year_tree.pack()

    def choice3(self):
        self.play_window = tk.Toplevel(window)
        self.play_window.title("Spotify-playlists where song is found")
        self.play_window.geometry("400x400")
        self.play_window.configure(bg=BACKGROUND_COLOR)


        self.play_label = tk.Label(self.play_window, text="Enter song:", bg=BACKGROUND_COLOR, fg="white")
        self.play_label.pack()
        self.play_entry = tk.Entry(self.play_window)
        self.play_entry.pack()

        self.songs_button = RoundedButton(self.play_window, text="Get Spotify-playlists", command=self.send_choice3, bg=BUTTON_COLOR, fg="white")
        self.songs_button.pack()

        pop_songs_play_label = tk.Label(self.play_window, text="Number of Spotify-Playlists:", bg=BACKGROUND_COLOR, fg="white")
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
        self.graph_window.configure(bg=BACKGROUND_COLOR)


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
window.configure(bg=BACKGROUND_COLOR) 

app = Application(window)

window.mainloop()

app.close_connection()