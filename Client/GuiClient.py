import tkinter as tk
import logging
import socket
import sys
import hashlib

class Application:
    def __init__(self, window):
        self.window = window
        self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.io_stream_server = self.socket_to_server.makefile(mode='rw')
        host = socket.gethostname()
        port = 9999

        logging.info("Making connection with server...")
        self.socket_to_server.connect((host, port))

        self.create_login_screen()

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
        # Unpack the login screen widgets
        self.username_label.pack_forget()
        self.username_entry.pack_forget()
        self.password_label.pack_forget()
        self.password_entry.pack_forget()
        self.login_button.pack_forget()

        # Create the main menu widgets
        self.choice1_button = tk.Button(self.window, text="Get popular songs of artist", command=self.choice1)
        self.choice1_button.pack()

        self.choice2_button = tk.Button(self.window, text="Most popular songs per year", command=self.choice2)
        self.choice2_button.pack()

    def choice1(self):
        artist_window = tk.Toplevel(window)
        artist_window.title("Artist")
        artist_label = tk.Label(window, text="Artist:")
        artist_label.pack()
        songs_button = tk.Button(window, text="Get popular songs")
        songs_button.pack()

    def choice2(self):
        pass  # Implement this method

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