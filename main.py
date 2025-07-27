import os
import re
import tempfile
import subprocess
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

def load_game_database():
    tree = ET.parse(xml_path)
    root = tree.getroot()
    game_map = {}
    for game in root.findall('game'):
        game_id = game.findtext('id')
        name = game.get('name')
        if game_id and name:
            game_map[game_id] = name
    return game_map

def find_files(directory, file_extension, option):

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and filename.endswith(file_extension):

            print(f"Current File: {filename}")

            if option == "1":
                game_id = get_iso_data(filepath)
                sort_rom(filepath, game_id, option, directory, filename)

            elif option == "2":
                game_id = get_wbfs_data(filepath)
                sort_rom(filepath, game_id, option, directory, filename)

def get_iso_data(filepath):
    with open(filepath, 'rb') as f:
        f.seek(0x000)
        game_id = f.read(6).decode('ascii', errors = 'ignore')
        f.seek(0x20)
        title_bytes = f.read(64)
        game_name = title_bytes.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
        print(f"Game name: {game_name}")
        print(f"Game ID: {game_id}")
        return game_id

def get_wbfs_data(filepath): # directory, filename):
    # filepath = os.path.join(directory, filename)
    with open(filepath, 'rb') as f:
        f.seek(0x200)  # Skip WBFS header to disc header
        game_id = f.read(6).decode('ascii', errors = 'ignore')
        f.seek(0x200 + 0x20)
        title_bytes = f.read(64)
        game_name = title_bytes.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
        print(f"Game name: {game_name}")
        print(f"Game ID: {game_id}\n")
    return game_id

def sort_rom(filepath, game_id, option, directory, filename):
    game_name = game_map.get(game_id)
    if game_name is None:
        print(f"[WARNING] Game ID {game_id} not found in XML. Skipping.")
        game_name = f"Unknown Game {game_id}"
    game_name = re.sub(r"\s*\(.*?\)", "", game_name)
    game_name = re.sub(r"[!/]", "", game_name)
    game_name = re.sub(r"[:/]", "", game_name)
    game_name = re.sub(r" &.*?;", "and", game_name)
    game_name = re.sub(r"\$.*?;", "s", game_name)
    game_name = re.sub(r"\s{2,}", " ", game_name)

    game_name = game_name.strip()

    folder_name = game_name + " [" + game_id + "]"

    temp_name = "temp.iso"

    if option == "1":
        os.rename(os.path.join(directory, filename), os.path.join(directory, temp_name))

        # Make the folder if it doesn't exist
        destination_folder = os.path.join(directory, folder_name)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.move(os.path.join(directory, temp_name), os.path.join(destination_folder, "game.iso"))
    elif option == "2":
        os.rename(os.path.join(directory, filename), os.path.join(directory, folder_name + ".wbfs"))


def main():
    global xml_path
    global game_map
    print("Please Choose the rom format.")
    print("1. GameCube (.iso)")
    print("2. Wii (.wbfs)")

    while True:
        option = input()
        if option == "1":
            file_extension = ".iso"
            break
        elif option == "2":
            file_extension = ".wbfs"
            break
        else:
            print("Invalid input. Please try again.")


    directory = select_directory()
    if not directory:
        print("No directory selected. Exiting.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))

    xml_path = os.path.join(script_dir, "wiitdb.xml")
    game_map = load_game_database()

    find_files(directory, file_extension, option)

main()

