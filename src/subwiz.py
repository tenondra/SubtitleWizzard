import argparse
import curses
import hashlib
import logging
import os
import pathlib
import platform
import requests
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# ==============
# CONSTANTS

HEADER = {
    "user-agent": "SubDB/1.0 (SubtitleWizzard:1.0; https://github.com/tenondra/SubtitleWizzard)"}
SUFFIX = '.srt'

# ==============


def get_pureName(fileName):
    return str(fileName).split('\\')[-1] if platform.system() == 'Windows' else str(fileName).split('/')[-1]


def iter_movies(directory):
    directory.iterdir()
    arr = pathlib.Path()
    logging.debug(arr)
    return []


def get_hash(name):
    readsize = 64 * 1024
    try:
        with open(name, 'rb') as f:
            # size = os.path.getsize(name)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
    except PermissionError:
        sys.exit()
    return hashlib.md5(data).hexdigest()


def get_url(action, mhash, language=''):
    # For development only
    return f"http://sandbox.thesubdb.com/?action={action}&hash={mhash}{language}"
    # For normal use-case
    # return f"http://api.thesubdb.com/?action={action}&hash={mhash}{language}"


def get_languages(filePath, mhash):
    request = requests.get(get_url('search', mhash), headers=HEADER)
    assert request.status_code == 200, f"Cannot find any suitable language for: {get_pureName(filePath)}"
    return request.text.split(',')


def save_file(filePath, request):
    with open(filePath.with_suffix('.srt'), 'wb') as fp:
        for chunk in request.iter_content(chunk_size=8192):
            if chunk:
                fp.write(chunk)


def get_sutitles(filePath, mhash, language):
    name = get_pureName(filePath)
    logging.debug(f"Name: {name}")
    request = requests.get(
        get_url('download', mhash, "&language=" + language), headers=HEADER)
    assert request.status_code == 200, f"Cannot download subtitles for: {name}"
    save_file(filePath, request)


def file_handle(filePath):
    mhash = get_hash(filePath)
    logging.debug(f"Filepath: {filePath}, md5 hash: {mhash}")
    langs = get_languages(filePath, mhash)
    logging.debug(f"Avail langs: {langs}")
    get_sutitles(filePath, mhash, "en")


def choose_file():
    root = tk.Tk()
    root.withdraw()
    file_handle(pathlib.Path(filedialog.askopenfilename()))


def choose_folder():
    root = tk.Tk()
    root.withdraw()
    dirPath = pathlib.Path(filedialog.askdirectory())
    movies = iter_movies(dirPath)
    for filePath in movies:
        file_handle(filePath)


def fpdialog():
    root = tk.Tk()
    root.title("Subtitle wizzard")
    frame = tk.Frame(root)
    frame.pack()

    file_button = tk.Button(frame,
                            text="Single File",
                            command=lambda:[choose_file(),root.destroy()],
                            width=20,
                            height=2,)
    file_button.pack(side=tk.LEFT)
    dir_button = tk.Button(frame,
                           text="Folder",
                           command=choose_folder,
                           width=20,
                           height=2)
    dir_button.pack(side=tk.LEFT)

    root.mainloop()


def init_logging(level):
    """Initialize loggers.

    :param level: Logging level.
    :type level: int
    """
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s]: %(message)s")

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s]: %(message)s',
        '%d.%m.%Y: %H%M%S')

    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)


def main(args):
    init_logging(logging.DEBUG)

    fpdialog()


def entry_point(*args):
    sys.exit(main(args))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
