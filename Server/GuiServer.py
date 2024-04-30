import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import socket
from queue import Queue
from threading import Thread
import tkinter as tk
from tkinter import *

from Server import Server
from ClientHandler import search_counts


LOGGED_USERS_PATH = "./Data/logged_users.txt"

class ServerWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.init_messages_queue()
        self.init_server()


    # Creation of init_window
    def init_window(self):
        frame = tk.Frame(self.master)
        frame.grid(pady=10)
        frame.configure(bg="#191414")
        self.master.title("Server")
        self.master.geometry("400x400")
        self.master.configure(bg="#191414")

        self.master.start_button = tk.Button(frame, text="Start server", command=self.Start_Window, bg="#1DB954", fg="white")
        self.master.start_button.grid(row=0, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        self.master.users_button = tk.Button(frame, text="Get logged in users", command=self.ingelogde_users, bg="#1DB954", fg="white")
        self.master.users_button.grid(row=1, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        self.master.popularity_button = tk.Button(frame, text="View searches", command=self.view_searches, bg="#1DB954", fg="white")
        self.master.popularity_button.grid(row=2, column=0, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)


    def Start_Window(self):
        self.start_window = tk.Toplevel(self.master)
        self.start_window.title("Register user")
        self.start_window.geometry("400x400")
        self.start_window.configure(bg="#191414")

        self.start_window.configure(bg="#191414")

        Label(self.start_window, text="Log-berichten server:", bg="#191414", fg="white").grid(row=0)
        self.start_window.scrollbar = Scrollbar(self.start_window, orient=VERTICAL)
        self.start_window.lstnumbers = Listbox(self.start_window, yscrollcommand=self.start_window.scrollbar.set, bg="#191414", fg="white")
        self.start_window.scrollbar.config(command=self.start_window.lstnumbers.yview)

        self.start_window.lstnumbers.grid(row=1, column=0, sticky=N + S + E + W)
        self.start_window.scrollbar.grid(row=1, column=1, sticky=N + S)

        self.start_window.btn_text = StringVar()
        self.start_window.btn_text.set("Start server")
        self.start_window.buttonServer = Button(self.start_window, textvariable=self.start_window.btn_text, command=self.start_stop_server, bg="#1DB954", fg="white")
        self.start_window.buttonServer.grid(row=3, column=0, columnspan=2, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        Grid.rowconfigure(self.start_window, 1, weight=1)
        Grid.columnconfigure(self.start_window, 0, weight=1)

    def ingelogde_users(self):
        users_window = tk.Toplevel(self.master)
        users_window.title("Logged-in Users")
        users_window.geometry("300x200")
        users_window.configure(bg="#191414")

        logged_users_label = Label(users_window, text="Logged-in Users", bg="#191414", fg="white")
        logged_users_label.pack()

        users_listbox = Listbox(users_window, bg="#191414", fg="white")
        users_listbox.pack(fill="both", expand=True)

        try:
            with open(LOGGED_USERS_PATH, "r") as file:
                logged_users = file.readlines()
                for user in logged_users:
                    users_listbox.insert(END, user.strip())
        except FileNotFoundError:
            users_listbox.insert(END, "No logged-in users")

        close_button = Button(users_window, text="Close", command=users_window.destroy, bg="#1DB954", fg="white")
        close_button.pack(pady=10)

    def view_searches(self):
        global search_counts
        searches_window = tk.Toplevel(self.master)
        searches_window.title("Searches")
        searches_window.geometry("300x200")
        searches_window.configure(bg="#191414")

        searches_title_label = Label(searches_window, text="Searches", bg="#191414", fg="white")
        searches_title_label.pack()

        for search_type, count in search_counts.items():
            searches_labeltype = Label(searches_window, text=search_type, bg="#191414", fg="white")
            searches_labeltype.pack(fill="both", expand=True)
            searches_labelcount = Label(searches_window, text=count, bg="#191414", fg="white")
            searches_labelcount.pack(fill="both", expand=True)

        close_button = Button(searches_window, text="Close", command=searches_window.destroy, bg="#1DB954", fg="white")
        close_button.pack(pady=10)


    def init_server(self):
        # server - init
        self.server = Server(socket.gethostname(), 9999, self.messages_queue)

    # def __del__(self):
    #     print("afsluiten server")
    #     self.afsluiten_server()

    def start_stop_server(self):
        if self.server.is_connected == True:
            self.server.close_server_socket()
            self.start_window.btn_text.set("Start server")
        else:
            self.server.init_server()
            self.server.start()             #thread!
            self.start_window.btn_text.set("Stop server")


    def afsluiten_server(self):
        if self.server != None:
            self.server.close_server_socket()
            self.messages_queue.put("CLOSE_SERVER")


    # QUEUE
    def init_messages_queue(self):
        self.messages_queue = Queue()
        t = Thread(target=self.print_messsages_from_queue, name="Thread-queue")
        t.start()

    def print_messsages_from_queue(self):
        message = self.messages_queue.get()
        while not "CLOSE_SERVER" in message:
            self.start_window.lstnumbers.insert(END, message)
            self.messages_queue.task_done()
            message = self.messages_queue.get()
