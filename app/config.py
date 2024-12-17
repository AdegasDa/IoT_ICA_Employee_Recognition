import json
import os

with open(os.path.join(os.path.dirname(__file__), "client_secret.json")) as config_file:
    config = json.load(config_file)