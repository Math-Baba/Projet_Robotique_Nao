# -*- coding: utf-8 -*-

import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "nao_config.py")

def save_ip(ip):
    with open(CONFIG_FILE, "w") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("ROBOT_IP = '{}'\n".format(ip))
        f.write("PORT = 9559\n")

def load_ip():
    try:
        from config.nao_config import ROBOT_IP
        return ROBOT_IP
    except:
        return None
