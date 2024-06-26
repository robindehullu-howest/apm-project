import os
import sys
import logging
import socket
from queue import Queue
from threading import Thread

import tkinter as tk
from tkinter import *

from Server import Server
from ClientHandler import SEARCH_COUNTS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGGED_USERS_PATH = "./Data/logged_users.txt"

BUTTON_COLOR = "#1DB954"
BACKGROUND_COLOR = "#191414"
BACKGROUND_COLOR_ENTRY = "#121212"

class ServerWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.init_messages_queue()

        self.start_window = None
        self.server = None

    def init_window(self):
        frame = tk.Frame(self.master)
        frame.grid(pady=10)
        frame.configure(bg=BACKGROUND_COLOR)
        self.master.title("Server")
        self.master.geometry("400x400")
        self.master.configure(bg=BACKGROUND_COLOR)

        button_font = ("Arial", 12, "bold")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.master.start_button = tk.Button(frame, text="Start server", command=self.start_server_window, bg=BUTTON_COLOR, fg="white", font=button_font)
        self.master.start_button.grid(row=0, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        self.master.users_button = tk.Button(frame, text="Get logged in users", command=self.active_users_window, bg=BUTTON_COLOR, fg="white", font=button_font)
        self.master.users_button.grid(row=1, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        self.master.popularity_button = tk.Button(frame, text="View searches", command=self.searches_window, bg=BUTTON_COLOR, fg="white", font=button_font)
        self.master.popularity_button.grid(row=2, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        self.master.broadcast_message_button = tk.Button(frame, text="Broadcast message", command=self.broadcast_message_window, bg=BUTTON_COLOR, fg="white", font=button_font)
        self.master.broadcast_message_button.grid(row=3, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)


    def start_server_window(self):
        start_window = self.__create_window("Start server", "400x400", BACKGROUND_COLOR)

        Label(start_window, text="Log-berichten server:", bg=BACKGROUND_COLOR, fg="white").grid(row=0)

        scrollbar = Scrollbar(start_window, orient=VERTICAL)
        lstnumbers = Listbox(start_window, yscrollcommand=scrollbar.set, bg=BACKGROUND_COLOR, fg="white")
        scrollbar.config(command=lstnumbers.yview)

        lstnumbers.grid(row=1, column=0, sticky=N + S + E + W)
        scrollbar.grid(row=1, column=1, sticky=N + S)

        btn_text = StringVar()
        btn_text.set("Start server")
        buttonServer = Button(start_window, textvariable=btn_text, command=self.start_stop_server, bg=BUTTON_COLOR, fg="white")
        buttonServer.grid(row=3, column=0, columnspan=2, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        Grid.rowconfigure(start_window, 1, weight=1)
        Grid.columnconfigure(start_window, 0, weight=1)

        self.start_window = start_window
        self.start_window.scrollbar = scrollbar
        self.start_window.lstnumbers = lstnumbers
        self.start_window.btn_text = btn_text
        self.start_window.buttonServer = buttonServer

        self.start_stop_server()

    def active_users_window(self):
        users_window = self.__create_window("Logged-in Users", "300x200", BACKGROUND_COLOR)

        logged_users_label = Label(users_window, text="Logged-in Users", bg=BACKGROUND_COLOR, fg="white")
        logged_users_label.pack()

        users_listbox = Listbox(users_window, bg=BACKGROUND_COLOR, fg="white")
        users_listbox.pack(fill="both", expand=True)

        try:
            with open(LOGGED_USERS_PATH, "r") as file:
                logged_users = file.readlines()
                for user in logged_users:
                    users_listbox.insert(END, user.strip())
        except FileNotFoundError:
            users_listbox.insert(END, "No logged-in users")

        close_button = Button(users_window, text="Close", command=users_window.destroy, bg=BUTTON_COLOR, fg="white")
        close_button.pack(pady=10)

    def searches_window(self):
        global SEARCH_COUNTS
        searches_window = self.__create_window("Searches", "300x200", BACKGROUND_COLOR)

        searches_title_label = Label(searches_window, text="Searches", bg=BACKGROUND_COLOR, fg="white")
        searches_title_label.pack()

        for search_type, count in SEARCH_COUNTS.items():
            searches_labeltype = Label(searches_window, text=search_type, bg=BACKGROUND_COLOR, fg="white")
            searches_labeltype.pack(fill="both", expand=True)
            searches_labelcount = Label(searches_window, text=count, bg=BACKGROUND_COLOR, fg="white")
            searches_labelcount.pack(fill="both", expand=True)

        close_button = Button(searches_window, text="Close", command=searches_window.destroy, bg=BUTTON_COLOR, fg="white")
        close_button.pack(pady=10)

    def broadcast_message_window(self):
        self.broadcast_window = self.__create_window("Broadcast message", "300x200", BACKGROUND_COLOR)

        self.broadcast_window.grid_rowconfigure(0, weight=1)
        self.broadcast_window.grid_rowconfigure(3, weight=1)
        self.broadcast_window.grid_columnconfigure(0, weight=1)
        self.broadcast_window.grid_columnconfigure(2, weight=1)

        message_label = Label(self.broadcast_window, text="Message:", bg=BACKGROUND_COLOR, fg="white")
        message_label.grid(row=1, column=1)

        message_entry = Entry(self.broadcast_window, fg="white", bg=BACKGROUND_COLOR_ENTRY)
        message_entry.grid(row=2, column=1)

        broadcast_button = Button(self.broadcast_window, text="Broadcast", command=lambda: self.broadcast_message(message_entry.get()), bg=BUTTON_COLOR, fg="white")
        broadcast_button.grid(row=3, column=1, pady=10)

    def broadcast_message(self, message):
        if self.server is not None:
            self.server.broadcast_message(message)
        self.broadcast_window.destroy()

    def start_server(self):
        self.server = Server(socket.gethostname(), 9999, self.messages_queue)
        self.server.start()

    def stop_server(self):
        if self.server is not None:
            self.server.close_server_socket()

    def start_stop_server(self):
        if self.server is not None:
            self.stop_server()
            self.start_window.btn_text.set("Start server")
        else:
            self.start_server()          #thread!
            self.start_window.btn_text.set("Stop server")

    def __create_window(self, title, geometry, bg_color):
        window = tk.Toplevel(self.master)
        window.title(title)
        window.geometry(geometry)
        window.configure(bg=bg_color)
        return window

    def __del__(self):
        self.messages_queue.put("CLOSE_WINDOW")


    # QUEUE
    def init_messages_queue(self):
        self.messages_queue = Queue()
        t = Thread(target=self.print_messsages_from_queue, name="Thread-queue")
        t.start()

    def print_messsages_from_queue(self):
        message = self.messages_queue.get()
        while not "CLOSE_WINDOW" in message:
            self.start_window.lstnumbers.insert(END, message)
            self.messages_queue.task_done()
            message = self.messages_queue.get()