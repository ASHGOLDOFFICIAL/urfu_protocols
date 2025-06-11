import pathlib


def read_file_content(file: pathlib.Path) -> str:
    with open(file, 'r') as f:
        return f.read()