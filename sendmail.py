import configparser

config = configparser.ConfigParser()
config.read("config.ini")

try:
    settings = config["SETTINGS"]
except:
    settings = {}

API = settings.get("APIKEY" , None)
from_email = settings.get("FROM" , "")
to_email = settings.get("TO" , "")