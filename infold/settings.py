from json import dumps, loads

current_settings = {} # holds the data of the settings file at any moment during game execution

settings_base = { # set containing the default settings when the file hasn't been created/is corrupted
    "language": "FR",
    "username": "Jean-Louis Jacques du Père, 3e du nom",
    "progression": "LNiveau1",
    "all_access": False,
    "has_selected_username": False
}

def read_settings():
    global current_settings

    try:
        with open("infold/data/settings.json", "r") as file:
            current_settings = loads(file.read()) # loads the content of the file into the current_settings value

    except: # settings file doesn't exist or is corrupted, loads the base data and creates the file
        current_settings = dict(settings_base)

        save_settings()

def save_settings():
    global current_settings

    with open("infold/data/settings.json", "w") as file:
        file.write(dumps(current_settings))

read_settings() # loads the data of the settings file