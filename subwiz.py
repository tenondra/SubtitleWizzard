import argparse
import curses
import hashlib
import logging
import os
import pathlib
import requests
import sys
import tkinter as tk
from tkinter import filedialog

# ==============
# CONSTANTS

HEADER = {
    "user-agent": "SubDB/1.0 (SubtitleWizzard:1.0; https://github.com/tenondra/SubtitleWizzard)"}
SUFFIX = '.srt'

# ==============


def fpdialog():
    root = tk.Tk()
    root.withdraw()
    return pathlib.Path(filedialog.askopenfilename())


def get_pureName(name):
    return str(name).split('/')[-1]


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        # size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()


def get_url(action, mhash, language=''):
    # return f"http://api.thesubdb.com/?action={action}&hash={mhash}{language}"
    return f"http://sandbox.thesubdb.com/?action={action}&hash={mhash}{language}"


def get_languages(filePath, mhash):
    request = requests.get(get_url('search', mhash), headers=HEADER)
    assert request.status_code == 200, logging.error(
        f"Cannot find any suitable language for: {get_pureName(filePath)}")
    return request.text.split(',')


def download(filePath, request):
    # NOTE the stream=True parameter below
    with open(filePath.with_suffix('.srt'), 'wb') as fp:
        for chunk in request.iter_content(chunk_size=8192):
            if chunk:
                fp.write(chunk)
                # f.flush()


def get_sutitles(filePath, mhash, language):
    name = get_pureName(filePath)
    logging.debug(f"Name: {name}")
    request = requests.get(
        get_url('download', mhash, "&language=" + language), headers=HEADER)
    assert request.status_code == 200, logging.error(
        f"Cannot download subtitles for: {name}")
    download(filePath, request)
    return name

# def prompt_lang():
#


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
    # args = parse_args(args)
    init_logging(logging.DEBUG)

    filePath = fpdialog()
    mhash = get_hash(filePath)
    logging.debug(f"Filepath: {filePath}, md5 hash: {mhash}")

    langs = get_languages(filePath, mhash)
    logging.debug(langs)
    subtitles = get_sutitles(filePath, mhash, "en")
    logging.debug(subtitles)


def parse_args(args=None):
    """Parse arguments from commandline.

    :param args: List of arguments. If None, then sys.argv is used.
    :type args: list
    :return: Parsed arguments.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__)
    return parser.parse_args(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
