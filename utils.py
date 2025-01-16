import pickle
import os

def save(data):
    with open("save_data.pkl", "wb") as f:
        pickle.dump(data, f)
        f.close()

def load_users():
    with open("save_data.pkl", "rb") as f:
        users = pickle.load(f)
    return users

def data_exists():
    if os.path.exists("save_data.pkl"):
        return True
    else: 
        return False
