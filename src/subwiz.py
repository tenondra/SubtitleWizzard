import argparse
import curses
import filetype
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

DEVELOPMENT = False
HEADER = {
    "user-agent": "SubDB/1.0 (SubtitleWizzard:1.0; \
         https://github.com/tenondra/SubtitleWizzard)"}
SUFFIX = '.srt'

# ==============


def get_pureName(filePath):
    """Return pure file name without full path.

    """
    return str(filePath).split('\\')[-1] if platform.system() == 'Windows' \
        else str(filePath).split('/')[-1]


def is_media(filePath):
    return True if filetype.video(str(filePath)) else False


def iter_directory(dirPath):
    """Iterates through a directory and its sub-directories and returns all movie files.

    """
    movies = []
    directory = dirPath.iterdir()
    for file in directory:
        if pathlib.Path(file).is_dir():
            movies += (iter_directory(file))
        else:
            if is_media(file):
                movies.append(file)
    logging.debug(movies)
    return movies


def get_hash(name):
    """Returns md5 hash of a movie file. Taken from thesubdb.com.

    """
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
    """Return subtitle database url in correct format.

    """
    return \
        f"http://sandbox.thesubdb.com/?action={action}&hash={mhash}{language}" \
        if DEVELOPMENT else \
        f"http://api.thesubdb.com/?action={action}&hash={mhash}{language}"


def get_languages(filePath, mhash):
    """Request subtitle languages from subtitle db.

    """
    url = get_url('search', mhash)
    try:
        request = requests.get(url, headers=HEADER)
    except requests.ConnectionError:
        messagebox.showwarning(
            title="Cannot connect", message=f"Unable to fetch url {url}")
        raise AssertionError("Unable to fetch url %s" % url)
    assert request.status_code == 200, messagebox.showwarning(
        title="No subtitles", message=f"Found no subtitles for: {get_pureName(filePath)}")
    return request.text.split(',')


def save_file(filePath, request):
    """Write output of subtitle request from db to a file.

    """
    with open(filePath.with_suffix('.srt'), 'wb') as fp:
        for chunk in request.iter_content(chunk_size=8192):
            if chunk:
                fp.write(chunk)


def get_sutitles(filePath, mhash, language):
    """Request subtitle file from subtitle db.

    """
    name = get_pureName(filePath)
    url = get_url('download', mhash, "&language=" + language)
    logging.debug(f"Name: {name}")
    try:
        request = requests.get(
            url, headers=HEADER)
    except requests.ConnectionError:
        messagebox.showwarning(
            title="Cannot connect", message=f"Unable to fetch url {url}")
        raise AssertionError(f"Unable to fetch url {url}")
    assert request.status_code == 200, messagebox.showwarning(
        title="Cannot download", message=f"Could not download subtitles for: {get_pureName(filePath)}")
    save_file(filePath, request)


def file_handle(filePath):
    """Handle processing of a movie. Get languages and get aproppriate subtitles.

    """
    mhash = get_hash(filePath)
    logging.debug(f"Filepath: {filePath}, md5 hash: {mhash}")
    langs = get_languages(filePath, mhash)
    logging.debug(f"Avail langs: {langs}")
    get_sutitles(filePath, mhash, "en")


def choose_file():
    """Let user choose a single file via gui.

    """
    root = tk.Tk()
    root.withdraw()
    filePath = pathlib.Path(filedialog.askopenfilename())
    assert filePath != pathlib.Path('.'), "Not a valid path"
    if is_media(filePath):
        file_handle(filePath)
    else:
        messagebox.showerror(title="Not a media file",
                             message="Selected file is not a valid media file")


def choose_folder():
    """Let user choose a single directory via gui.

    """
    root = tk.Tk()
    root.withdraw()
    dirPath = pathlib.Path(filedialog.askdirectory())
    logging.debug(f"Dirpath:{dirPath}")
    assert dirPath != pathlib.Path('.'), "Not a valid path"
    movies = iter_directory(dirPath)
    for filePath in movies:
        try:
            file_handle(filePath)
        except AssertionError:
            logging.warning(f"Could not process {get_pureName(filePath)}")


def fpdialog():
    """Handle file dialogs and user interface.

    """
    # Setup tkinter gui
    root = tk.Tk()
    root.title("Subtitle wizzard")
    # frame = tk.Frame(root)
    # frame.pack()

    # Setup buttons and check boxes
    file_button = tk.Button(root,
                            text="Single File",
                            command=lambda: [root.destroy(), choose_file()],
                            width=20,
                            height=2,)
    file_button.pack(side=tk.LEFT)
    dir_button = tk.Button(root,
                           text="Folder",
                           command=lambda: [root.destroy(), choose_folder()],
                           width=20,
                           height=2)
    dir_button.pack(side=tk.LEFT)

    # Update the window with content and wait for user input
    root.update_idletasks()
    root.update()
    root.wait_window()


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
    # sys.exit(main(args))
    main(args)


if __name__ == "__main__":
    # sys.exit(main(sys.argv[1:]))
    main(sys.argv[1:])
