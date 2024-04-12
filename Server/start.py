import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
from tkinter import *

from GuiServer import ServerWindow

def callback():
    print("Active threads:")
    for thread in threading.enumerate():
        print(f">Thread name is {thread.name}.")
    gui_server.afsluiten_server()
    root.destroy()

root = Tk()
root.geometry("600x500")
gui_server = ServerWindow(root)
root.protocol("WM_DELETE_WINDOW", callback)
root.mainloop()