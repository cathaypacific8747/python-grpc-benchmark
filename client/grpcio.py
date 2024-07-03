import grpc.aio  # type: ignore

from . import test_pb2, test_pb2_grpc


async def say_hello(name: str, n_calls: int = 1) -> str:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = test_pb2_grpc.GreeterStub(channel)
        msg = ""
        for _ in range(n_calls):
            msg += (await stub.SayHello(test_pb2.HelloRequest(name=name))).message
        return msg


async def stream_numbers(count: int, n_calls: int = 1) -> list[int]:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = test_pb2_grpc.GreeterStub(channel)
        r: list[int] = []
        for _ in range(n_calls):
            async for reply in stub.StreamNumbers(test_pb2.NumberRequest(count=count)):
                r.append(reply.number)
        return r
