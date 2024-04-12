import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import hashlib

from Models.User import User

username = "admin"
password = "admin"

def register_user(username: str, password: str):
    password = hashlib.sha256(password.encode()).hexdigest()
    user = User(username, password)
    my_writer_obj = open("../Data/users.txt", mode='ab')
    pickle.dump(user, my_writer_obj)
    my_writer_obj.close()

register_user(username, password)
