import os
import zipfile
import tempfile
from pathlib import Path
import unicodedata
import re
import urllib.parse
from typing import List, Tuple
import sys
import io

import requests
import click

from .version import __version__


def get_latest_version_str():
    r = requests.get('https://pypi.python.org/pypi/texercise/json')
    response = r.json()
    return response['info']['version']


upload_ignore = (
    '*/.*',
    '*/CMakeFiles',
    '*/Makefile',
    '*/cmake_install.cmake',
    '*/CMakeCache.txt',
    '*.o',
)


def fn_match_recursive(fp: Path, ignores, root: Path = None):
    if root is None:
        root = fp
    rel_fp = Path("/" + str(fp.relative_to(root)))
    if any(rel_fp.match(ignore) for ignore in ignores):
        return []
    elif fp.is_file():
        return [fp]
    elif fp.is_dir():
        item_lists = (fn_match_recursive(it, ignores, root) for it in fp.glob("*"))
        return (item for sublist in item_lists for item in sublist)
    else:
        return []


def parse_version(version_str):
    major, minor, micro = [int(s) for s in version_str.split(".")]
    return major, minor, micro


base_url = 'http://texercise.rasmushaugaard.dk'


def validate_email(_, __, value):
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
        raise click.UsageError('Incorrect email address given')
    else:
        return value


def url_quote(inp):
    if isinstance(inp, (List, Tuple)):
        return [url_quote(a) for a in inp]
    return urllib.parse.quote(inp)


class Context:
    NONE = None
    COURSE = 'course'
    EXERCISE = 'exercise'


def _load_config(fp: Path):
    try:
        with fp.open() as f:
            course, user_type, email, token = [l.strip() for l in f.readlines()]
    except Exception as e:
        print("Could not read .texercise file")
        raise e
    return course, user_type, email, token


def load_config():
    folder = Path().absolute()
    fp = folder / ".texercise"
    if fp.exists():
        return "course", folder, None, _load_config(fp)
    while folder.parent != folder:
        child_folder = folder
        folder = folder.parent
        fp = folder / ".texercise"
        if fp.exists():
            return "exercise", folder, child_folder, _load_config(fp)
    return None, None, None, (None, None, None, None)


def zip_files(files: List[Path], root: Path, max_size_kb=0, size_e_message='File too large'):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fp in files:
            zf.write(fp, fp.relative_to(root))
    if max_size_kb:
        size_kb = zip_buffer.getbuffer().nbytes / 1024
        if size_kb > max_size_kb:
            print(size_e_message, '{}/{} kB'.format(int(size_kb), int(max_size_kb)))
            sys.exit()
    zip_buffer.seek(0)
    return zip_buffer


def valid_filesystem_name(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value)
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


def duration_format(s):
    M = 60
    H = M * 60
    D = H * 24
    days = int(s // D)
    s -= days * D
    hours = int(s // H)
    s -= hours * H
    minutes = int(s // M)
    s -= minutes * M
    seconds = int(s // 1)
    milliseconds = int((s - seconds) * 1000)
    return '{:2d}d {:2d}h {:2d}m {:2d}.{:3d}s'.format(days, hours, minutes, seconds, milliseconds)


def get_echo_exercise_folder():
    return Path(__file__).parent / 'echo_exercise'
