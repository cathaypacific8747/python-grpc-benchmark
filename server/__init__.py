import contextlib
import os
from pathlib import Path

from utils import remember_cwd

base_dir = Path(__file__).parent


def clean():
    with remember_cwd():
        os.chdir(base_dir)
        os.system("./clean")


def build():
    with remember_cwd():
        os.chdir(base_dir)
        os.system("./build")


@contextlib.contextmanager
def run():
    with remember_cwd():
        os.chdir(base_dir)
        os.system(". ./config")
        os.system("docker kill $CONTAINER_NAME > /dev/null 2>&1")
        os.system("./run > /dev/null 2>&1")

    try:
        yield
    finally:
        print("killing server")
        os.system("docker kill $CONTAINER_NAME > /dev/null 2>&1")
