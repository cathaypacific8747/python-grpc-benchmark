import asyncio
import time
from typing import Literal

import click
import matplotlib.pyplot as plt
import numpy as np
import psutil

import client
import server


@click.group()
def cli():
    pass


@cli.command()
def build():
    client.clean()
    client.build()
    server.clean()
    server.build()


Stats = tuple[float, float]  # time, memory


async def get_stats(f) -> Stats:
    process = psutil.Process()
    start_mem = process.memory_info().rss
    start_time = time.perf_counter()
    await f
    end_time = time.perf_counter()
    end_mem = process.memory_info().rss
    return end_time - start_time, end_mem - start_mem


StatsCollection = dict[Literal["grpcio", "grpclib"], dict[int, Stats]]


async def main():
    import client.grpcio
    import client.grpclib

    with server.run():
        n_requests = 1000
        stats: StatsCollection = {
            "grpcio": {},
            "grpclib": {},
        }
        for msg_size in np.linspace(4, 2**16, num=200, dtype=int):
            print(f"running {msg_size=}")
            msg = "A" * msg_size
            stats["grpcio"][msg_size] = await get_stats(
                client.grpcio.say_hello(msg, n_requests)
            )
            stats["grpclib"][msg_size] = await get_stats(
                client.grpclib.say_hello(msg, n_requests)
            )
        plot(
            stats,
            n_requests,
            xlabel="Length of string",
            ylabel="Throughput (characters per second)",
            title="say_hello",
        )

        n_requests = 1000
        stats = {
            "grpcio": {},
            "grpclib": {},
        }
        for count in np.linspace(4, 2**8, num=200, dtype=int):
            print(f"running {count=}")
            stats["grpcio"][count] = await get_stats(
                client.grpcio.stream_numbers(count, n_requests)
            )
            stats["grpclib"][count] = await get_stats(
                client.grpclib.stream_numbers(count, n_requests)
            )
        plot(
            stats,
            n_requests,
            xlabel="Number of integers streamed per request",
            ylabel="Throughput (integers per second)",
            title="stream_numbers",
        )


def plot(
    stats: StatsCollection, n_requests: int, *, xlabel: str, ylabel: str, title: str
):
    ax: plt.Axes
    fig, ax = plt.subplots(figsize=(16, 9), layout="tight")
    fig.suptitle(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    rps: dict[Literal["grpcio", "grpclib"], np.ndarray] = {}
    for library, stat in stats.items():
        x = list(stat.keys())
        time_, mem = zip(*stat.values())
        rps[library] = n_requests * np.array(x) / np.array(time_)
        ax.plot(x, rps[library], label=library)
    speedup = rps["grpcio"] / rps["grpclib"]
    print(f"speedup: {speedup}")

    fig.savefig(f"time_{title}.png", dpi=300)
    plt.legend()
    plt.show()


@cli.command()
def run():
    asyncio.run(main())


if __name__ == "__main__":
    cli()
