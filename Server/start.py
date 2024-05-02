import os
import sys
import threading
from tkinter import Tk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from GuiServer import ServerWindow

def cleanup():
    print("Active threads:")
    for thread in threading.enumerate():
        print(f">Thread name is {thread.name}.")
    gui_server.stop_server()
    root.destroy()

root = Tk()
root.geometry("600x500")

gui_server = ServerWindow(root)

root.protocol("WM_DELETE_WINDOW", cleanup)

root.mainloop()