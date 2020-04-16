import argparse
import hashlib
import logging
import os
import pathlib
import requests
import sys
import tkinter as tk
from tkinter import filedialog


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()


def get_url(action, mhash, language=''):
    return f"http://api.thesubdb.com/?action={action}&hash={mhash}{language}"


def get_languages(name, mhash):
    r = requests.get(get_url('search', mhash))
    assert r.status_code == 200, logging.error(
        f"Cannot find any suitable language for: {name}")


def get_subs(name, mhash, language):
    r = requests.get(get_url('download', mhash, f"&language={language}"))
    assert r.status_code == 200, logging.error(
        f"Cannot download subtitles for: {name}")


def prompt_lang():
    pass


# def subs_download():
#     pass


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

    root = tk.Tk()
    root.withdraw()

    filePath = pathlib.Path(filedialog.askopenfilename())
    mhash = get_hash(filePath)
    logging.debug(f"Filepath: {filePath}, md5 hash: {mhash}")

    langs = prompt_lang()
    header = {
        "user-agent": "SubDB/1.0 (SubtitleBOX/1.0; https://github.com/sameera-madushan/SubtitleBOX.git)"}


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
