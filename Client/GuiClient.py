import io
import os
import tkinter as tk
from tkinter import ttk
import logging
import socket
import hashlib
from PIL import Image, ImageTk
from queue import Queue
import base64
import json
import threading

BUTTON_COLOR = "#1DB954"
BUTTON_COLOR_ENTER = "#1ED760"
BACKGROUND_COLOR = "#191414"
BACKGROUND_COLOR_ENTRY = "#121212"
MAIN_BUTTON_FONT = ("Arial", 14, "bold")
LABEL_FONT = ("Arial", 11)

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

        self.keep_threads_alive = True
        self.message_queue = Queue()

        logging.info("Making connection with server...")
        self.socket_to_server.connect((host, port))

        self.window.geometry("600x400")
        self.create_login_screen()

        self.start_receiving_messages()

    def clear_table(self, treeview):
        for item in treeview.get_children():
            treeview.delete(item)


################################################# Server communication #################################################

    def receive_message(self):
        while self.keep_threads_alive:
            message = self.io_stream_server.readline().rstrip('\n')
            logging.info(f"Message from server: {message}")
            self.message_queue.put(message)

    def start_receiving_messages(self):
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()
        process_thread = threading.Thread(target=self.process_message)
        process_thread.start()

    def process_message(self):
        while self.keep_threads_alive:
            topic = self.message_queue.get()
            
            if topic == "CLOSE":
                self.close_connection()
            if topic == "BROADCAST":
                message = self.message_queue.get()
                self.process_broadcast_message(message)
            if topic == "LOGIN":
                login_reply = self.message_queue.get()
                self.process_login_reply(login_reply)
            if topic == "REGISTER":
                register_reply = self.message_queue.get()
                self.process_register_reply(register_reply)
            if topic == "ARTIST":
                popular_songs = self.message_queue.get()
                self.process_artist_reply(popular_songs)
            if topic == "YEAR":
                pop_songs = self.message_queue.get()
                self.process_year_reply(pop_songs)
            if topic == "PLAYLIST":
                playlist_count = self.message_queue.get()
                self.process_playlist_reply(playlist_count)
            if topic == "GRAPH":
                image = self.message_queue.get()
                self.process_graph_reply(image)

    def process_broadcast_message(self, message):
        self.create_broadcast_popup(message)

    def process_login_reply(self, login_reply):
        if login_reply == "Login successful":
            self.create_main_menu()

    def process_register_reply(self, register_reply):
        if register_reply == "Register successful" and self.register_window is not None:
            self.register_window.destroy()

    def process_artist_reply(self, popular_songs):
        popular_songs = popular_songs.split(';') 

        self.clear_table(self.pop_songs_artist_tree)

        for index, song in enumerate(popular_songs, start=1):
            self.pop_songs_artist_tree.insert('', 'end',text=index, values=[song])

    def process_year_reply(self, pop_songs):
        self.clear_table(self.pop_songs_year_tree)  # vorige opvraging verwijderen
        try:
            pop_songs_json = json.loads(pop_songs)
            for index, (song, artists) in enumerate(pop_songs_json.items(), start=1):
                self.pop_songs_year_tree.insert('', 'end', text=index, values=[song, artists])
        except Exception as e:
            self.pop_songs_year_tree.insert('', 'end', values=[pop_songs])  # Insert error message directly into treeview
            logging.error(f"Error: {e}")

    def process_playlist_reply(self, playlist_count):
        if playlist_count == "No playlists found.":
            self.pop_songs_play["text"] = playlist_count
            logging.info("No playlists found.")
        else:
            self.pop_songs_play["text"] = playlist_count
            logging.info(f"Number of Spotify-Playlists: {playlist_count}")

    def process_graph_reply(self, img_string):
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

    def send_login_info(self):
        identifier = self.identifier_entry.get()
        password = hashlib.sha256(self.login_password_entry.get().encode()).hexdigest()

        self.io_stream_server.write("LOGIN\n")
        self.io_stream_server.write(f"{identifier}\n")
        self.io_stream_server.write(f"{password}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")

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

    def send_choice1(self):
        artist = self.artist_entry.get()
        self.io_stream_server.write("ARTIST\n")
        self.io_stream_server.write(f"{artist}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")

    def send_choice2(self):
        year = self.year_entry.get()
        self.io_stream_server.write("YEAR\n")
        self.io_stream_server.write(f"{year}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")

    def send_choice3(self):
        song = self.play_entry.get()
        self.io_stream_server.write("PLAYLIST\n")
        self.io_stream_server.write(f"{song}\n")
        self.io_stream_server.flush()

        logging.info("Waiting for answer from server...")

    def send_choice4(self):
        self.io_stream_server.write("GRAPH\n")
        self.io_stream_server.flush()

        logging.info("Waiting for graph from server...")


################################################# Window creation #################################################

    def create_broadcast_popup(self, message):
        broadcast_window = tk.Toplevel(self.window)
        broadcast_window.title("Broadcast message")
        broadcast_window.geometry("300x200")
        broadcast_window.configure(bg=BACKGROUND_COLOR)

        broadcast_window.grid_rowconfigure(0, weight=1)
        broadcast_window.grid_rowconfigure(4, weight=1)
        broadcast_window.grid_columnconfigure(0, weight=1)
        broadcast_window.grid_columnconfigure(2, weight=1)

        title_font = ("Arial", 14, "bold")
        message_font = ("Arial", 11, "italic")
        button_font = ("Arial", 11, "bold")

        admin_label = tk.Label(broadcast_window, text="Message from Server Admin:", bg=BACKGROUND_COLOR, fg="white", font=title_font)
        admin_label.grid(row=1, column=1, pady=25)

        message_label = tk.Label(broadcast_window, text=message, bg="white", fg="black", font=message_font, padx=2, pady=5, wraplength=250, background=BACKGROUND_COLOR_ENTRY, fg="white")
        message_label.grid(row=2, column=1)

        close_button = tk.Button(broadcast_window, text="Close", command=broadcast_window.destroy, bg=BUTTON_COLOR, fg="white", font=button_font)
        close_button.grid(row=3, column=1, pady=25)


    def create_login_screen(self):
        frame = tk.Frame(self.window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.identifier_label = tk.Label(frame, text="Username or email:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.identifier_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.identifier_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.identifier_entry.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.password_label = tk.Label(frame, text="Password:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.password_label.grid(row=2, column=0, pady=(5, 2), sticky="w")

        self.login_password_entry = tk.Entry(frame, show="*", background=BACKGROUND_COLOR_ENTRY, fg="white")
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

        frame = tk.Frame(self.register_window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.register_window.grid_rowconfigure(0, weight=1)
        self.register_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.register_username_label = tk.Label(frame, text="Username:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.register_username_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.register_username_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.register_username_entry.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.register_nickname_label = tk.Label(frame, text="Nickname:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.register_nickname_label.grid(row=2, column=0, pady=(5, 2), sticky="w")

        self.register_nickname_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.register_nickname_entry.grid(row=3, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.register_email_label = tk.Label(frame, text="Email:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.register_email_label.grid(row=4, column=0, pady=(5, 2), sticky="w")

        self.register_email_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.register_email_entry.grid(row=5, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.register_password_label = tk.Label(frame, text="Password:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.register_password_label.grid(row=6, column=0, pady=(5, 2), sticky="w")

        self.register_password_entry = tk.Entry(frame, show="*", background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.register_password_entry.grid(row=7, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.register_button = RoundedButton(frame, text="Register", command=self.send_register_info, bg=BUTTON_COLOR, fg="white")
        self.register_button.grid(row=8, column=0, pady=5)



    def create_main_menu(self):
        self.identifier_label.pack_forget()
        self.identifier_entry.pack_forget()
        self.password_label.pack_forget()
        self.login_password_entry.pack_forget()
        self.login_button.pack_forget()
        self.register_window_button.pack_forget()
    
        self.window.geometry("1000x600")
    
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, "Images", "spotify-logo.png")
        self.img = ImageTk.PhotoImage(Image.open(image_path))
        self.img_label = tk.Label(self.window, image=self.img, bg=BACKGROUND_COLOR)
        self.img_label.grid(row=0, column=0, columnspan=2, pady=5)
    
        self.choice1_button = RoundedButton(self.window, text="Get popular songs of artist", command=self.choice1, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=MAIN_BUTTON_FONT)
        self.choice1_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
        self.choice2_button = RoundedButton(self.window, text="Most popular songs per year", command=self.choice2, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=MAIN_BUTTON_FONT)
        self.choice2_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    
        self.choice3_button = RoundedButton(self.window, text="Number of Spotify-playlists where song is found", command=self.choice3, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=MAIN_BUTTON_FONT)
        self.choice3_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    
        self.choice4_button = RoundedButton(self.window, text="Graph of total streams per year", command=self.send_choice4, bg=BUTTON_COLOR, fg="white", height=3, width=3, font=MAIN_BUTTON_FONT)
        self.choice4_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
    
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)


################################################# Button functions/windows #################################################

    def choice1(self):
        self.artist_window = tk.Toplevel(window)
        self.artist_window.title("Artist")
        self.artist_window.geometry("800x400")
        self.artist_window.configure(bg=BACKGROUND_COLOR)

        frame = tk.Frame(self.artist_window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.artist_window.grid_rowconfigure(0, weight=1)
        self.artist_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)


        self.artist_label = tk.Label(frame, text="Artist:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.artist_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.artist_entry = tk.Entry(frame, width=2, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.artist_entry.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.songs_button = RoundedButton(frame, text="Get popular songs for artist", command=self.send_choice1, bg=BUTTON_COLOR, fg="white")
        self.songs_button.grid(row=2, column=0, pady=(5, 2), padx=5, sticky="ew")


        pop_songs_artist_label = tk.Label(frame, text="Popular Songs:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        pop_songs_artist_label.grid(row=3, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.pop_songs_artist_tree = ttk.Treeview(frame, columns=('Number','Popular Songs'))
        self.pop_songs_artist_tree.heading('#0', text='Number')
        self.pop_songs_artist_tree.heading('#1', text='Popular Songs')
        self.pop_songs_artist_tree.column('#2', width=0, stretch=tk.NO)
        self.pop_songs_artist_tree.grid(row=4, column=0, pady=(0, 5), padx=5, sticky="ew")


    def choice2(self):
        self.year_window = tk.Toplevel(window)
        self.year_window.title("popular songs (year)")
        self.year_window.geometry("800x400")
        self.year_window.configure(bg=BACKGROUND_COLOR)

        frame = tk.Frame(self.year_window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.year_window.grid_rowconfigure(0, weight=1)
        self.year_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.year_label = tk.Label(frame, text="Enter year:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.year_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.year_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.year_entry.grid(row=1, column=0, pady=(0, 5), sticky="ew")
        
        self.songs_button = RoundedButton(frame, text="Get popular songs", command=self.send_choice2, bg=BUTTON_COLOR, fg="white")
        self.songs_button.grid(row=2, column=0, pady=(5, 2), sticky="ew")


        pop_songs_year_label = tk.Label(frame, text="Popular Songs:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        pop_songs_year_label.grid(row=3, column=0, pady=(5, 2), sticky="ew")

        self.pop_songs_year_tree = ttk.Treeview(frame, columns=('Number','Popular Songs','Artist(s)'))
        self.pop_songs_year_tree.heading('#0', text='Number')
        self.pop_songs_year_tree.heading('#1', text='Popular Songs')
        self.pop_songs_year_tree.heading('#2', text='Artist(s)')
        self.pop_songs_year_tree.column('#3', width=0, stretch=tk.NO)
        self.pop_songs_year_tree.grid(row=4, column=0, pady=(0, 5), sticky="ew")


    def choice3(self):
        self.play_window = tk.Toplevel(window)
        self.play_window.title("Spotify-playlists where song is found")
        self.play_window.geometry("400x400")
        self.play_window.configure(bg=BACKGROUND_COLOR)

        frame = tk.Frame(self.play_window, bg=BACKGROUND_COLOR)
        frame.grid(pady=10)

        self.play_window.grid_rowconfigure(0, weight=1)
        self.play_window.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)


        self.play_label = tk.Label(frame, text="Enter song:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        self.play_label.grid(row=0, column=0, pady=(5, 2), sticky="w")

        self.play_entry = tk.Entry(frame, background=BACKGROUND_COLOR_ENTRY, fg="white")
        self.play_entry.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")

        self.songs_button = RoundedButton(frame, text="Get Spotify-playlists", command=self.send_choice3, bg=BUTTON_COLOR, fg="white")
        self.songs_button.grid(row=2, column=0, pady=5)

        pop_songs_play_label = tk.Label(frame, text="Number of Spotify-Playlists:", bg=BACKGROUND_COLOR, fg="white", font=LABEL_FONT)
        pop_songs_play_label.grid(row=3, column=0, pady=(5, 2), sticky="w")

        self.pop_songs_play = tk.Label(frame, background=BACKGROUND_COLOR, fg="white", font=("Arial", 16, "bold"))
        self.pop_songs_play.grid(row=4, column=0, pady=(5, 2), sticky="ew")


    def close_connection(self):
        logging.info("Close connection with server...")
        self.keep_threads_alive = False
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