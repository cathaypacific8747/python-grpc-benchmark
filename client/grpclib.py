from grpclib.client import Channel

from . import test_grpc, test_pb2


async def say_hello(name: str, n_calls: int = 1) -> str:
    async with Channel("localhost", 50051) as channel:
        stub = test_grpc.GreeterStub(channel)
        msg = ""
        for _ in range(n_calls):
            msg += (await stub.SayHello(test_pb2.HelloRequest(name=name))).message
        return msg


async def stream_numbers(count: int, n_calls: int = 1) -> list[int]:
    async with Channel("localhost", 50051) as channel:
        stub = test_grpc.GreeterStub(channel)
        r: list[int] = []
        for _ in range(n_calls):
            async with stub.StreamNumbers.open() as stream:
                await stream.send_message(test_pb2.NumberRequest(count=count), end=True)
                async for reply in stream:
                    r.append(reply.number)
        return r
