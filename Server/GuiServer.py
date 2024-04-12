import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import socket
from queue import Queue
from threading import Thread
from tkinter import *

from Server import Server


class ServerWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.init_messages_queue()
        self.init_server()


    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Log-berichten server:").grid(row=0)
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.lstnumbers = Listbox(self, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lstnumbers.yview)

        self.lstnumbers.grid(row=1, column=0, sticky=N + S + E + W)
        self.scrollbar.grid(row=1, column=1, sticky=N + S)

        self.btn_text = StringVar()
        self.btn_text.set("Start server")
        self.buttonServer = Button(self, textvariable=self.btn_text, command=self.start_stop_server)
        self.buttonServer.grid(row=3, column=0, columnspan=2, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

    def init_server(self):
        # server - init
        self.server = Server(socket.gethostname(), 9999, self.messages_queue)

    # def __del__(self):
    #     print("afsluiten server")
    #     self.afsluiten_server()

    def start_stop_server(self):
        if self.server.is_connected == True:
            self.server.close_server_socket()
            self.btn_text.set("Start server")
        else:
            self.server.init_server()
            self.server.start()             #thread!
            self.btn_text.set("Stop server")


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
            self.lstnumbers.insert(END, message)
            self.messages_queue.task_done()
            message = self.messages_queue.get()
