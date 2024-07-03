import contextlib
import os


@contextlib.contextmanager
def remember_cwd():
    curr_dir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curr_dir)
