from pathlib import Path

from utils import remember_cwd

base_dir = Path(__file__).parent


def clean():
    for file in base_dir.glob("**/test_*.py*"):
        file.unlink()


def build():
    import os

    from grpc_tools import protoc  # type: ignore

    with remember_cwd():
        os.chdir(base_dir.parent)
        out_dir = "client"
        protoc.main(
            (
                "-I.",
                f"--python_out={out_dir}",
                f"--pyi_out={out_dir}",
                f"--grpc_python_out={out_dir}",
                f"--grpclib_python_out={out_dir}",
                "test.proto",
            )
        )
        # make absolute imports relative
        with open(f"{out_dir}/test_pb2_grpc.py", "r+") as f:
            data = f.read().replace(
                "import test_pb2 as test__pb2",
                "from . import test_pb2 as test__pb2",
            )
            f.seek(0)
            f.write(data)
            f.truncate()

        with open(f"{out_dir}/test_grpc.py", "r+") as f:
            data = f.read().replace(
                "import test_pb2",
                "from . import test_pb2",
            )
            f.seek(0)
            f.write(data)
            f.truncate()
