import os
import re
import shutil
import hashlib
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
from os import mkdir, rename
from xml.etree.ElementPath import get_parent_map
#!/usr/bin/env python

def select_directory():
    root = tk.Tk()
    root.withdraw()
    selected_dir = filedialog.askdirectory(title="Select the ROM directory")
    return selected_dir

def find_files(directory):

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and filename.endswith(".iso"):

            print(f"Current File: {filename}")

            with open(filepath, 'rb') as f:
                sha1 = hashlib.sha1()
                for chunk in iter(lambda: f.read(8192), b''):
                    sha1.update(chunk)
            filehash = sha1.hexdigest()

            print("Hash: {}".format(filehash))
            find_data(filehash, directory, filename)

def find_data(filehash, directory, filename):


    xml_path = os.path.join(directory, "wiitdb.xml")

    # Parse the XML file
    try:
        tree = ET.parse(xml_path)
        print("File parsed successfully.")
        root = tree.getroot()
    except ET.ParseError as e:
        print("Parse error:", e)
        return
    except FileNotFoundError as e:
        print("File not found:", e)
        return
    except Exception as e:
        print("An error occurred:", e)
        return


    if root is not None:
        print("Root tag:", root.tag)
    else:
        print("No root element found.")
        return

    for game in root.findall('game'):
        for rom in game.findall('rom'):
            sha1 = rom.get('sha1')

            if sha1 == filehash:
                game_name = game.get('name')
                print(f"Game: {game_name}")
                game_id = game.findtext('id')
                if game_id:
                    print(f"ID: {game_id}")
                game_name = re.sub(r"\s*\(.*?\)", "", game_name)
                game_name = re.sub(r"[!/]", "", game_name)
                game_name = re.sub(r"[:/]", "", game_name)
                game_name = re.sub(r"&.*?;", "and", game_name)
                game_name = re.sub(r"\$.*?;", "s", game_name)
                game_name = game_name.strip()

                folder_name = game_name + " [" + game_id + "]"

                temp_name = f"{filehash[:8]}.tmp.iso"
                os.rename(os.path.join(directory, filename), os.path.join(directory, temp_name))


                # Make the folder if it doesn't exist
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

                shutil.move(os.path.join(directory, temp_name), os.path.join(folder_name, "game.iso"))


def main():
    directory = select_directory()
    if not directory:
        print("No directory selected. Exiting.")
        return
    find_files(directory)


main()

