import tkinter as tk
import logging
import socket
import sys

logging.basicConfig(level=logging.INFO)

logging.info("Making connection with server...")

# create a socket object
socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()
port = 9999

# connection to hostname on the port.
socket_to_server.connect((host, port))

def login():
    # Create the username label and entry
    username_label = tk.Label(window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

    # Create the password label and entry
    password_label = tk.Label(window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    # Create the login button
    login_button = tk.Button(window, text="Login", command=login)
    login_button.config(command=show_choices)
    login_button.pack()

    username = username_entry.get()
    password = password_entry.get()
    io_stream_server = socket_to_server.makefile(mode='rw')
    io_stream_server.write(f"{username}\n")
    io_stream_server.write(f"{password}\n")
    io_stream_server.flush()

    print("Waiting for answer from server...")
    message = io_stream_server.readline().rstrip('\n')
    print(f"Message from server: {message}")

def show_choices():
    # Create a new window for choices
    choices_window = tk.Toplevel(window)
    choices_window.title("Top Spotify Songs")

    # Create the choices/buttons
    choice1_button = tk.Button(choices_window, text="Get popular songs of artist")
    choice1_button.config(command=choice1)
    choice1_button.pack()

    choice2_button = tk.Button(choices_window, text="Most popular songs per year")
    choice2_button.pack()

def choice1():
    artist_window = tk.Toplevel(window)
    artist_window.title("Artist")
    artist_label = tk.Label(window, text="Artist:")
    artist_label.pack()
    songs_button = tk.Button(window, text="Get popular songs")
    songs_button.pack()


logging.info("Close connection with server...")

# Create the main window
window = tk.Tk()
window.title("GUI Client")
login()


# Start the main loop
window.mainloop()

socket_to_server.close()
